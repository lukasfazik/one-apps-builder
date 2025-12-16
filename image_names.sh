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

architecture="x64"
language="en_US"
prefix=""
date=$(date +"%Y-%m-%d")
suffix=" ($date)"
declare -A names

# Windows 10
version="22H2"

names["windows10Home"]="${prefix}Windows 10 Home ${version} ${architecture} ${language}${suffix}"
names["windows10HomeN"]="${prefix}Windows 10 Home N ${version} ${architecture} ${language}${suffix}"
names["windows10HomeSingleLanguage"]="${prefix}Windows 10 Home Single Language ${version} ${architecture} ${language}${suffix}"
names["windows10Pro"]="${prefix}Windows 10 Pro ${version} ${architecture} ${language}${suffix}"
names["windows10ProN"]="${prefix}Windows 10 Pro N ${version} ${architecture} ${language}${suffix}"
names["windows10ProWorkstations"]="${prefix}Windows 10 Pro for Workstations ${version} ${architecture} ${language}${suffix}"
names["windows10ProWorkstationsN"]="${prefix}Windows 10 Pro for Workstations N ${version} ${architecture} ${language}${suffix}"
names["windows10ProEducation"]="${prefix}Windows 10 Pro Education ${version} ${architecture} ${language}${suffix}"
names["windows10ProEducationN"]="${prefix}Windows 10 Pro Education N ${version} ${architecture} ${language}${suffix}"
names["windows10Education"]="${prefix}Windows 10 Education ${version} ${architecture} ${language}${suffix}"
names["windows10EducationN"]="${prefix}Windows 10 Education N ${version} ${architecture} ${language}${suffix}"
names["windows10Enterprise"]="${prefix}Windows 10 Enterprise ${version} ${architecture} ${language}${suffix}"
names["windows10EnterpriseN"]="${prefix}Windows 10 Enterprise N ${version} ${architecture} ${language}${suffix}"

# Windows 10 LTSC Eneterprise
names["windows10EnterpriseLTSC2015"]="${prefix}Windows 10 Enterprise LTSC 2015 ${architecture} ${language}${suffix}"
names["windows10EnterpriseLTSC2016"]="${prefix}Windows 10 Enterprise LTSC 2016 ${architecture} ${language}${suffix}"
names["windows10EnterpriseLTSC2019"]="${prefix}Windows 10 Enterprise LTSC 2019 ${architecture} ${language}${suffix}"
names["windows10EnterpriseLTSC2021"]="${prefix}Windows 10 Enterprise LTSC 2021 ${architecture} ${language}${suffix}"
# Windows 11
version="24H2"

names["windows11Home"]="${prefix}Windows 11 Home ${version} ${architecture} ${language}${suffix}"
names["windows11HomeN"]="${prefix}Windows 11 Home N ${version} ${architecture} ${language}${suffix}"
names["windows11HomeSingleLanguage"]="${prefix}Windows 11 Home Single Language ${version} ${architecture} ${language}${suffix}"
names["windows11Pro"]="${prefix}Windows 11 Pro ${version} ${architecture} ${language}${suffix}"
names["windows11ProN"]="${prefix}Windows 11 Pro N ${version} ${architecture} ${language}${suffix}"
names["windows11ProWorkstations"]="${prefix}Windows 11 Pro for Workstations ${version} ${architecture} ${language}${suffix}"
names["windows11ProWorkstationsN"]="${prefix}Windows 11 Pro for Workstations N ${version} ${architecture} ${language}${suffix}"
names["windows11ProEducation"]="${prefix}Windows 11 Pro Education ${version} ${architecture} ${language}${suffix}"
names["windows11ProEducationN"]="${prefix}Windows 11 Pro Education N ${version} ${architecture} ${language}${suffix}"
names["windows11Education"]="${prefix}Windows 11 Education ${version} ${architecture} ${language}${suffix}"
names["windows11EducationN"]="${prefix}Windows 11 Education N ${version} ${architecture} ${language}${suffix}"
names["windows11Enterprise"]="${prefix}Windows 11 Enterprise ${version} ${architecture} ${language}${suffix}"
names["windows11EnterpriseN"]="${prefix}Windows 11 Enterprise N ${version} ${architecture} ${language}${suffix}"

# Windows 10 LTSC Enterprise
names["windows11EnterpriseLTSC2024"]="${prefix}Windows 11 Enterprise LTSC 2024 ${architecture} ${language}${suffix}"

# Windows Server 2016

names["windows2016Essentials"]="${prefix}Windows Server 2016 Essentials ${architecture} ${language}${suffix}"
names["windows2016Standard"]="${prefix}Windows Server 2016 Standard GUI ${architecture} ${language}${suffix}"
names["windows2016StandardCore"]="${prefix}Windows Server 2016 Standard Core ${architecture} ${language}${suffix}"
names["windows2016Datacenter"]="${prefix}Windows Server 2016 Datacenter GUI ${architecture} ${language}${suffix}"
names["windows2016DatacenterCore"]="${prefix}Windows Server 2016 Datacenter Core ${architecture} ${language}${suffix}"

# Windows Server 2019

names["windows2019Essentials"]="${prefix}Windows Server 2019 Essentials ${architecture} ${language}${suffix}"
names["windows2019Standard"]="${prefix}Windows Server 2019 Standard GUI ${architecture} ${language}${suffix}"
names["windows2019StandardCore"]="${prefix}Windows Server 2019 Standard Core ${architecture} ${language}${suffix}"
names["windows2019Datacenter"]="${prefix}Windows Server 2019 Datacenter GUI ${architecture} ${language}${suffix}"
names["windows2019DatacenterCore"]="${prefix}Windows Server 2019 Datacenter Core ${architecture} ${language}${suffix}"

# Windows Server 2022

names["windows2022Standard"]="${prefix}Windows Server 2022 Standard GUI ${architecture} ${language}${suffix}"
names["windows2022StandardCore"]="${prefix}Windows Server 2022 Standard Core ${architecture} ${language}${suffix}"
names["windows2022Datacenter"]="${prefix}Windows Server 2022 Datacenter GUI ${architecture} ${language}${suffix}"
names["windows2022DatacenterCore"]="${prefix}Windows Server 2022 Datacenter Core ${architecture} ${language}${suffix}"

# Windows Server 2025

names["windows2025Standard"]="${prefix}Windows Server 2025 Standard GUI ${architecture} ${language}${suffix}"
names["windows2025StandardCore"]="${prefix}Windows Server 2025 Standard Core ${architecture} ${language}${suffix}"
names["windows2025Datacenter"]="${prefix}Windows Server 2025 Datacenter GUI ${architecture} ${language}${suffix}"
names["windows2025DatacenterCore"]="${prefix}Windows Server 2025 Datacenter Core ${architecture} ${language}${suffix}"
