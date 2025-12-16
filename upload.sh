#!/bin/bash

# Copyright 2025 Lukáš Fázik
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# image server parameters
http_host=$(hostname -f)
http_port="8080"
http_base_url="http://$http_host:$http_port"

# OpenNebula cloud parameters
datastore="100"

# Get image names
source ./image_names.sh

# helper functions

write_stderr () {
    echo "$1" >&2
}


run_command ()
{
    local container_id="$1"
    local command="$2"
    write_stderr "Executing command: $command"
    podman exec -i "$container_id" bash -c "$command"
}


build_container ()
{
    local podman_image_tag="$1"
    write_stderr "Building image $podman_image_tag"

    podman build --pull --no-cache -t "$podman_image_tag" . >&2 || {
        write_stderr "Image build failed"
        return 1
    }

    write_stderr "Image build finished"
    return 0
}


create_container ()
{
    local podman_image_tag image_dir work_dir
    podman_image_tag="$1"
    image_dir=$(realpath -m "$2")
    work_dir="/images"

    # OpenNebula parameters
    local one_xml_rpc default_one_auth_file one_auth_file one_auth_dir one_auth_filename
    one_xml_rpc="$ONE_XMLRPC"
    default_one_auth_file="$HOME/.one/one_auth"
    one_auth_file=$(realpath "${ONE_AUTH:-$default_one_auth_file}")
    one_auth_dir=$(dirname "$one_auth_file")
    one_auth_filename=$(basename "$one_auth_file")

    # build container
    podman image exists "$podman_image_tag" || {
        write_stderr "Podman image $podman_image_tag does not exists" &&
        build_container "$podman_image_tag" ||
        return 1
    }
    
    # run container
    write_stderr "Creating container from image $podman_image_tag"
    container_id=$(podman run -d -it \
        --workdir "$work_dir" \
        -p "$http_port:$http_port" \
        --volume "$one_auth_dir:/root/.one:ro,z" \
        --volume "$image_dir:$work_dir:ro,z" \
        -e "ONE_XMLRPC=$one_xml_rpc" \
        -e "ONE_AUTH=/root/.one/$one_auth_filename" \
    "$podman_image_tag"
    ) || {
        write_stderr "Failed to create container"
        return 1
    }

    echo "$container_id"
    return 0
}


destroy_container ()
{
    local container_id="$1"

    write_stderr "Destroying container $container_id"

    {
        podman kill "$container_id" > /dev/null &&
        podman rm "$container_id" > /dev/null
    } || {
        write_stderr "Failed to destroy container $container_id"
        return 1
    }

    write_stderr "Container destroyed successfully"
    return 0
}


start_web_server ()
{
    local container_id="$1"
    local port="$2"
    write_stderr "Starting temporary web server on port $port"
    {
        podman exec -d "$container_id" python3 -m http.server "$port" > /dev/null
        
    } || {
        write_stderr "Failed to start web server"
        return 1
    }
    return 0
}


# checks the state of image in OpenNebula datastore
check_image ()
{
    local container_id image_id result image_state
    container_id="$1"
    image_id="$2"

    # Get the image state
    result=$(podman exec -i "$container_id" oneimage list \
        -f "id=$image_id" \
        --no-header \
        --no-pager \
        --no-expand \
        --csv \
        -l stat
    ) || {
        write_stderr "Failed to check state for image $image_id"
        return 1
    }

    # Parse image state
    if [ -n "$result" ];then
        image_state=$(echo -n "$result" | tr -d '\r')
    else
        image_state="not found"
    fi

    echo "$image_state"
    return 0
}

# Creates image in OpenNebula datastore and tells OpenNebula to download it from this image server
upload_image ()
{
    local container_id="$1"
    local image_name="$2"
    local full_name="$3"
    local image_path="$http_base_url/${image_name}.qcow2"
    local podman_command="oneimage create --name \"$full_name\" --path \"$image_path\" --datastore $datastore"
    local podman_output
    podman_output=$(run_command "$container_id" "$podman_command") || {
        write_stderr "Failed to create image $full_name with path $image_path"
        return 1
    }
    
    image_id=$(echo -n "$podman_output" | cut -f 2 -d ' ' | tr -d '\r')

    echo "$image_id"
    return 0
}


# Waits until image is downloaded by OpenNebula
wait_for_image ()
{
    
    local container_id="$1"
    local image_id="$2"
    local image_state

    echo -n "Waiting for image $image_id" >&2
    while [ "$(check_image "$container_id" "$image_id")" != "rdy" ];do
        image_state=$(check_image "$container_id" "$image_id")
        sleep 1
        echo -n " ." >&2
        if [ "$image_state" == "err" ];then
            echo -e "\nWait failed, image $image_id is in error state"
            return 1
        fi
    done
    echo -e "\nDone" >&2
    return 0
}


# Destroys failed image
destroy_image ()
{
    local container_id="$1"
    local image_id="$2"
    write_stderr "Deleting image $image_id"
    run_command "$container_id" "oneimage delete $image_id" > /dev/null
    return 0
}


# Creates VM template
create_template ()
{
    local container_id="$1"
    local IMAGE_ID="$2"
    local TEMPLATE_NAME="$3"
    export IMAGE_ID TEMPLATE_NAME
    template=$(envsubst '$TEMPLATE_NAME $IMAGE_ID' < template.tmpl)
    write_stderr "Creating template $TEMPLATE_NAME with image $IMAGE_ID"
    
    echo "$template" | run_command "$container_id" "onetemplate create" > /dev/null || {
        write_stderr "Failed to create template"
        return 1
    }

    write_stderr "Template created successfully"
    return 0
}


# Used when path in argument points to single qcow2 image
upload_single_file ()
{
    local file_path directory_path image_name full_name container_id podman_image_tag
    podman_image_tag="one-apps-builder"
    file_path=$(realpath -m "$1")
    directory_path=$(dirname "$file_path")
    image_name=$(basename "$file_path" .qcow2)
    full_name="${names[$image_name]}"

    write_stderr "Uploading $image_name as $full_name"

    container_id=$(create_container "$podman_image_tag" "$directory_path") || return 1
    
    start_web_server "$container_id" "$http_port" || {
        destroy_container "$container_id"
        return 1
    }

    image_id=$(upload_image "$container_id" "$image_name" "$full_name") || {
        write_stderr "Upload failed"
        destroy_container "$container_id"
        return 1
    }
    
    wait_for_image "$container_id" "$image_id" || {
        destroy_image "$container_id" "$image_id"
        destroy_container "$container_id"
        return 1
    }
    
    create_template "$container_id" "$image_id" "$full_name" || {
        destroy_image "$container_id" "$image_id"
        destroy_container "$container_id"
        return 1
    }

    write_stderr "Uploaded $image_name as $full_name"
    destroy_container "$container_id" || return 1
    return 0
}


# Uploads all qcow2 images from a directory in argument
upload_directory ()
{
    local directory_path
    directory_path=$(realpath -m "$1")

    write_stderr "Uploading all *.qcow2 images in $directory_path"
    for file_path in "$directory_path"/*.qcow2;do
        upload_single_file "$file_path" || return 1
    done
}


main ()
{
    # parse arguments
    [ -f "$1" ] && {
        { upload_single_file "$1" && return 0; } || return 1
    }
        
    [ -d "$1" ] && {
        { upload_directory "$1" && return 0; } || return 1
    }

    write_stderr "No file path provided"
    return 1
}


main "$@"
