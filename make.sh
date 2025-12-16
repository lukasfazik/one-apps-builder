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
    local podman_image_tag container_id one_apps_dir iso_dir build_dir export_dir
    podman_image_tag="$1"
    one_apps_dir=$(realpath -m "$2")
    build_dir=$(realpath -m "$3")
    export_dir=$(realpath -m "$4")
    iso_dir=$(realpath -m "$5")
    context_linux_out_dir=$(realpath -m "$build_dir/context_linux/out")
    context_windows_out_dir=$(realpath -m "$build_dir/context_windows/out")

    mkdir -p "$build_dir" || return 1
    mkdir -p "$export_dir" || return 1
    mkdir -p "$context_linux_out_dir" || return 1
    mkdir -p "$context_windows_out_dir" || return 1

    # build container image if does not exists
    podman image exists "$podman_image_tag" || {
        write_stderr "Podman image $podman_image_tag does not exists" &&
        build_container "$podman_image_tag" ||
        return 1
    }
    
    # run container
    write_stderr "Creating container from image $podman_image_tag"
    container_id=$(podman run -d -i \
        --workdir /one-apps \
        --device /dev/kvm \
        -p 127.0.0.1:5900-6000:5900-6000 \
        --volume "$one_apps_dir:/one-apps:O"  \
        --volume "$build_dir:/one-apps/build:rw,z" \
        --volume "$context_windows_out_dir:/one-apps/context-windows/out:rw,z" \
        --volume "$context_linux_out_dir:/one-apps/context-linux/out:rw,z" \
        --volume "$export_dir:/one-apps/export:rw,z" \
        --volume "$iso_dir:/one-apps/packer/windows/iso:ro,z" \
        "$podman_image_tag"
    ) || { 
        write_stderr "Failed to create container"
        return 1
    }

    write_stderr "Container created successfully"
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


cleanup ()
{
    local build_dir
    build_dir=$(realpath -m "$1")
    write_stderr "Cleaning up build direcotry subtree: $build_dir"
    rm -rf "$build_dir"
    return 0
}


build_context ()
{
    write_stderr "Building context"
    local container_id="$1"
    run_command "$container_id" "make context-iso"
}


# This were some aspirations to do a job system for multiple builds at the same time
build_images ()
{
    local container_id="$1"
    local images="$2"
    for image_name in $images;do
         build_single_image "$container_id" "$image_name" &
    done
    wait
}


build_single_image ()
{
    local container_id="$1"
    local image_name="$2"

    write_stderr "Building image $image_name"
    run_command "$container_id" "make $image_name" || {
        write_stderr "Failed to build image $image_name"
        return 1
    }

    write_stderr "Image build done"
    return 0
}


main ()
{
    local podman_image_tag="one-apps-builder"
    local image_names="$*"
    local build_dir="/var/tmp/xfazik/build"
    local export_dir="/var/tmp/xfazik/export"
    local iso_dir="/var/tmp/xfazik/iso"
    local one_apps_dir="/home/xfazik/github/one-apps"
    local retval="0"
    
    # Exit if no image names provided
    [ -z "$image_names" ] && {
        write_stderr "No image names provided"
        return 1
    }

    # Create container, build context and build images
    {
        container_id=$(create_container "$podman_image_tag" "$one_apps_dir" "$build_dir" "$export_dir" "$iso_dir") &&
        build_context "$container_id" &&
        build_images "$container_id" "$image_names"
    } || {
            # Cleanup non-complete build
            cleanup "$build_dir"
            retval="1"
    }

    # Clean up container
    destroy_container "$container_id" || retval="1"
    return "$retval"
}


main "$@"
