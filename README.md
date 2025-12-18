# one-apps-builder

> **⚠️ WARNING: The `docker` container engine is currently broken and does not work with this CI/CD pipeline. Please use `podman` as the container engine. Attempts to use `docker` will result in failed builds.**

This repository provides a CI/CD setup for building [one-apps](https://github.com/OpenNebula/one-apps) project images in an automated pipeline. The pipeline is designed to be flexible, supporting user-defined inputs and customizations, and is intended for use with OpenNebula environments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [CI/CD Pipeline](#cicd-pipeline)
  - [User Inputs](#user-inputs)
  - [Modifying the one-apps Submodule](#modifying-the-one-apps-submodule)
- [OpenNebula Runner Registration](#opennebula-runner-registration)
- [Additional Notes](#additional-notes)
- [Security](#security)
- [Build Data and Artefact Storage](#build-data-and-artefact-storage)

## Overview

- **Automated Image Building:** Uses GitLab CI/CD to build Linux and Windows images for the one-apps project.
- **User Inputs:** The pipeline supports user-supplied parameters to customize builds.
- **Submodule Support:** The `one-apps` project is included as a submodule and can be modified as needed.
- **Containerfiles Included:** The repository contains all required containerfiles (Dockerfiles) for the build process, located in the `containers/` directory. These must be built and pushed to your container registry before first use by running the `build-containers` job.
- **OpenNebula Integration:** Built images are intended for deployment in OpenNebula.
- **Runner Template:** The repository contains the runner template for the build process.

## Prerequisites

- **Container Registry Required:** The pipeline requires access to a container registry to store and retrieve the custom build images. Make sure your GitLab project or environment is configured with a suitable registry and credentials.
- **Required CI/CD Variables:**
  - `ONE_XMLRPC`: URL of the OpenNebula XML-RPC API endpoint. This variable must be set for the pipeline to interact with your OpenNebula instance.
  - `ONE_AUTH`: A hidden, protected, and masked file variable containing the OpenNebula credentials in the format `user:password` or `user:token`. This is required for authentication with the OpenNebula API and should be securely managed in your CI/CD settings. **This variable must be masked and hidden, and should only be available to protected branches.**

## CI/CD Pipeline

The pipeline is defined in `.gitlab-ci.yml` and consists of several stages:

1. **build-containers:** Builds required container images.
2. **prepare-dependencies:** Prepares build contexts and downloads dependencies.
3. **build-images:** Builds the actual VM images using Packer and Makefiles.
4. **deploy-images:** Deploys built images to the target environment.
5. **cleanup:** Cleans up temporary files and artifacts.
5. **cleanup:** Cleans up temporary files and artefacts.
6. **delete-images:** (Manual) Deletes images and templates from OpenNebula.

### User Inputs

The pipeline supports the following user inputs, which can be set as pipeline variables. The `distro_name`, `distro_versions`, and `distro_editions` variables are combined to create build targets defined in the `one-apps/Makefile.config` file.

 - `pipeline_type`: Type of pipeline run (`build-containers` or `build-images`, default: `build-images`).
 - `image_datastore_id`: Target OpenNebula datastore ID for image upload (default: `100`).
 - `image_name_prefix`: Prefix for generated image names (default: empty).
 - `image_name_suffix`: Suffix for generated image names (default: ` $CI_PIPELINE_ID`).
- `distro_name`: The base name of the distribution (e.g., `ubuntu`, `debian`, `windows`). **For all Windows builds, this value must be `windows`**, as this is used to trigger the correct pipeline jobs.
- `distro_versions`: An array of distribution versions to build (e.g., `["12", "13"]` for Debian).
- `distro_editions`: An array of distribution editions (e.g., `["Pro", "Education"]` for Windows, or `["", "min"]` for Ubuntu). An empty string `""` can be used if there is no edition.
- `remove_artefacts`: Whether to remove build artefacts from the runner after deployment (`true`/`false`, default: `true`).
- `debug`: Enable more verbose information in CI/CD job output (`true`/`false`).

These inputs are referenced in the pipeline and can be set via the GitLab UI or API when triggering a pipeline.

**How Build Targets are Created:**

The pipeline concatenates the three `distro` variables to form a `make` target. For example:
- To build `windows11Pro` and `windows11Education`:
  - `distro_name`: `windows`
  - `distro_versions`: `["11"]`
  - `distro_editions`: `["Pro", "Education"]`
- To build `debian12` and `debian13`:
  - `distro_name`: `debian`
  - `distro_versions`: `["12", "13"]`
  - `distro_editions`: `[""]`
- To build `ubuntu2204` and `ubuntu2204min`:
  - `distro_name`: `ubuntu`
  - `distro_versions`: `["2204"]`
  - `distro_editions`: `["", "min"]`

Refer to the `one-apps/Makefile.config` file for a full list of available build targets.

### Modifying the one-apps Submodule

The `one-apps` directory is included as a git submodule. By default, the submodule points to a downstream repository maintained by the Faculty of Informatics, Masaryk University (MU), which may contain customizations specific to this environment. You can make local modifications to this submodule to customize the build process or add new features. After making changes, ensure you commit and push updates to the submodule as needed.

Alternatively, you can point the submodule to a different repository, such as the original [one-apps](https://github.com/OpenNebula/one-apps) repository, your own fork, or any compatible upstream. This allows you to easily track upstream changes or use a custom version of one-apps as required for your environment.

## OpenNebula Runner Registration

> **Note:** The provided runner setup scripts and templates are tested and configured for a **Debian 13** base system. The `runner/start_script.sh` uses Debian-specific package management (`apt-get`) and the `runner/vm_template.tmpl` defaults to a `Debian 13.0.0` image. While other Debian-based systems may work, they are not guaranteed to be compatible without modification.

To use the CI/CD pipeline with OpenNebula, you must register a custom runner. This involves setting up a VM template in OpenNebula with a custom startup script.

**Instructions:**

1. **Obtain the runner start script:**
    - The script is located at `runner/start_script.sh` in this repository.

2. **Encode the script in base64:**

    ```sh
    base64 -w 0 runner/start_script.sh
    ```

3. **Register the template in OpenNebula:**
    - Create a VM template in OpenNebula.
    - Copy contents of `runner/vm_template.tmpl` into it.
    - Set the `START_SCRIPT_64` attribute to the base64 output from the previous step.
    - **Important:** Configure the runner to run only on protected branches in your GitLab project. Protected branches restrict access to sensitive variables (like `ONE_AUTH`) and help prevent unauthorized use of credentials. If you are using a fork, ensure protected branches are set up in your fork as well.

4. **Instantiate the template in OpenNebula:**

     - Launch a new VM instance from the registered template.
     - When instantiating, provide the required runner configuration parameters as template inputs. The following inputs are supported:

        | Variable           | Type    | Description                                 | Default Value                    |
        |--------------------|---------|---------------------------------------------|----------------------------------|
        | `CI_SERVER_TOKEN`  | string  | GitLab runner registration token (required) |                                  |
        | `CI_SERVER_URL`    | string  | GitLab CI server URL (required)             | `https://gitlab.fi.muni.cz`      |
        | `CONCURRENT_JOBS`  | number  | Number of concurrent jobs to run (optional) | `1`                              |
        | `CONTAINER_ENGINE` | list    | Container engine to use (required)          | `podman` (`podman`, `docker`)    |

     - **Resource Recommendations:**  
          - Allocate at least **2 GB RAM** for the runner itself, plus an **additional 4 GB RAM and 4 CPU cores** for each parallel build you plan to run. Consider extra CPU and RAM for the runner process if running multiple builds concurrently.
          - **Disk Space:** Builds are stored on the main OS drive during the build process. Ensure there is enough free space for the OS image you are building.  
                - For **Windows builds**, a minimum of **32 GB free disk space per parallel build** is recommended, plus extra space for the Windows ISO files, which will be cached on the runner.
                - For Linux builds, ensure sufficient space for the base image, build artifacts, and any dependencies.

This step ensures the runner VM is configured with the correct GitLab server, token, and container engine, and is ready to execute CI/CD jobs as defined in this project pipeline.

This configuration ensures that the runner initialization script executes upon VM startup, installing the GitLab Runner package with the specified container runtime, configuring udev rules, and registering the runner.

## Repository Structure

- `containers/` — Containerfiles (Dockerfiles) for all build and deploy images.
- `one-apps/` — The one-apps submodule (can be pointed to any compatible repo).
- `runner/` — Scripts and templates for registering Gitlab runner.
- `deploy_image.py`, `delete_images.py` — Scripts for image deployment and cleanup.
- `.gitlab-ci.yml` — Main CI/CD pipeline definition.

## Additional Notes

- Ensure your OpenNebula environment is properly configured to accept and run the generated images.
- For advanced usage or troubleshooting, refer to the scripts and Makefiles in the `one-apps` repository.
- The pipeline is designed to be extensible; you can add new stages or customize existing ones as needed.

## Security

- **Unprivileged Containers:** All containers (except the deploy container) run as an unprivileged user at runtime. The deploy container requires elevated privileges for block device operations and is mapped to UID of the `gitlab-runner` user.
- **Unprivileged GitLab Runner:** The GitLab Runner service itself runs as the unprivileged `gitlab-runner` user (not root). Both rootless Podman and rootless Docker are supported and configured for the runner.
- **Device Access:** Containers have access to `/dev/kvm` for hardware virtualization and the entire `/dev/` tree is mounted inside the containers to support VM image operations.
- **Udev Rules:** Udev rules are set to allow read/write access to `/dev/sd[b-z]*` and `/dev/sd[a-z][a-z]*` block devices (i.e., all disks except `/dev/sda`) for the `gitlab-runner` group. This is required for direct disk operations during image builds, but ensures the system disk is not exposed to the runner.
- **Credential Security:** The CI/CD variable `ONE_AUTH` is always masked and hidden, and is only available to protected branches. Protected branches in GitLab restrict access to sensitive variables and prevent unauthorized use of credentials. If you are using a fork of this repository, make sure to configure protected branches in your fork as well to maintain security.

## Build Data and Artefact Storage

- **No CI/CD Artefacts:** Build artefacts (such as VM images) are not stored as GitLab artefacts due to their large file sizes.
- **Cache Usage:** The CI/CD cache is used for caching VirtIO driver downloads and context builds. This improves build speed and reduces redundant downloads.
- **/cache Volume:** The `/cache` directory inside the container is not an anonymous volume. It is mapped to `/home/gitlab-runner/runner-cache` on the runner VM, ensuring cache persistence across parallel jobs and pipelines.
- **/mnt/data Volume:** The `/mnt/data` directory inside the container is mapped to `/home/gitlab-runner/runner-data` on the runner VM. This directory stores all build artefacts, including finished (exported) images, organized in subfolders by pipeline ID (e.g., `/mnt/data/<pipeline_id>/export`).
- **Packer Caching:**
  - `packer_cache` directory is used for caching ISO/source disk downloads, reducing repeated downloads for subsequent builds.
  - `packer_plugins` directory is used for caching Packer plugins, improving build start times.

This storage strategy ensures that large build outputs and caches persist across parallel job runs, while keeping the CI/CD system scalable and performant.
