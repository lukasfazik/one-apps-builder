class ImageNames:
    def __init__(self, prefix: str="", architecture: str="", language: str="", suffix: str="") -> None:
        self._names = {
            # Windows 10
            "windows10Home": f"{prefix}Windows 10 Home 22H2 {architecture} {language}{suffix}",
            "windows10HomeN": f"{prefix}Windows 10 Home N 22H2 {architecture} {language}{suffix}",
            "windows10HomeSingleLanguage": f"{prefix}Windows 10 Home Single Language 22H2 {architecture} {language}{suffix}",
            "windows10Pro": f"{prefix}Windows 10 Pro 22H2 {architecture} {language}{suffix}",
            "windows10ProN": f"{prefix}Windows 10 Pro N 22H2 {architecture} {language}{suffix}",
            "windows10ProWorkstations": f"{prefix}Windows 10 Pro for Workstations 22H2 {architecture} {language}{suffix}",
            "windows10ProWorkstationsN": f"{prefix}Windows 10 Pro for Workstations N 22H2 {architecture} {language}{suffix}",
            "windows10ProEducation": f"{prefix}Windows 10 Pro Education 22H2 {architecture} {language}{suffix}",
            "windows10ProEducationN": f"{prefix}Windows 10 Pro Education N 22H2 {architecture} {language}{suffix}",
            "windows10Education": f"{prefix}Windows 10 Education 22H2 {architecture} {language}{suffix}",
            "windows10EducationN": f"{prefix}Windows 10 Education N 22H2 {architecture} {language}{suffix}",
            "windows10Enterprise": f"{prefix}Windows 10 Enterprise 22H2 {architecture} {language}{suffix}",
            "windows10EnterpriseN": f"{prefix}Windows 10 Enterprise N 22H2 {architecture} {language}{suffix}",

            # Windows 10 LTSC Enterprise
            "windows10EnterpriseLTSC2015": f"{prefix}Windows 10 Enterprise LTSC 2015 {architecture} {language}{suffix}",
            "windows10EnterpriseLTSC2016": f"{prefix}Windows 10 Enterprise LTSC 2016 {architecture} {language}{suffix}",
            "windows10EnterpriseLTSC2019": f"{prefix}Windows 10 Enterprise LTSC 2019 {architecture} {language}{suffix}",
            "windows10EnterpriseLTSC2021": f"{prefix}Windows 10 Enterprise LTSC 2021 {architecture} {language}{suffix}",

            # Windows 11
            "windows11Home": f"{prefix}Windows 11 Home 25H2 {architecture} {language}{suffix}",
            "windows11HomeN": f"{prefix}Windows 11 Home N 25H2 {architecture} {language}{suffix}",
            "windows11HomeSingleLanguage": f"{prefix}Windows 11 Home Single Language 25H2 {architecture} {language}{suffix}",
            "windows11Pro": f"{prefix}Windows 11 Pro 25H2 {architecture} {language}{suffix}",
            "windows11ProN": f"{prefix}Windows 11 Pro N 25H2 {architecture} {language}{suffix}",
            "windows11ProWorkstations": f"{prefix}Windows 11 Pro for Workstations 25H2 {architecture} {language}{suffix}",
            "windows11ProWorkstationsN": f"{prefix}Windows 11 Pro for Workstations N 25H2 {architecture} {language}{suffix}",
            "windows11ProEducation": f"{prefix}Windows 11 Pro Education 25H2 {architecture} {language}{suffix}",
            "windows11ProEducationN": f"{prefix}Windows 11 Pro Education N 25H2 {architecture} {language}{suffix}",
            "windows11Education": f"{prefix}Windows 11 Education 25H2 {architecture} {language}{suffix}",
            "windows11EducationN": f"{prefix}Windows 11 Education N 25H2 {architecture} {language}{suffix}",
            "windows11Enterprise": f"{prefix}Windows 11 Enterprise 25H2 {architecture} {language}{suffix}",
            "windows11EnterpriseN": f"{prefix}Windows 11 Enterprise N 25H2 {architecture} {language}{suffix}",

            # Windows 11 LTSC Enterprise
            "windows11EnterpriseLTSC2024": f"{prefix}Windows 11 Enterprise LTSC 2024 {architecture} {language}{suffix}",

            # Windows Server 2016
            "windows2016Essentials": f"{prefix}Windows Server 2016 Essentials {architecture} {language}{suffix}",
            "windows2016Standard": f"{prefix}Windows Server 2016 Standard GUI {architecture} {language}{suffix}",
            "windows2016StandardCore": f"{prefix}Windows Server 2016 Standard Core {architecture} {language}{suffix}",
            "windows2016Datacenter": f"{prefix}Windows Server 2016 Datacenter GUI {architecture} {language}{suffix}",
            "windows2016DatacenterCore": f"{prefix}Windows Server 2016 Datacenter Core {architecture} {language}{suffix}",

            # Windows Server 2019
            "windows2019Essentials": f"{prefix}Windows Server 2019 Essentials {architecture} {language}{suffix}",
            "windows2019Standard": f"{prefix}Windows Server 2019 Standard GUI {architecture} {language}{suffix}",
            "windows2019StandardCore": f"{prefix}Windows Server 2019 Standard Core {architecture} {language}{suffix}",
            "windows2019Datacenter": f"{prefix}Windows Server 2019 Datacenter GUI {architecture} {language}{suffix}",
            "windows2019DatacenterCore": f"{prefix}Windows Server 2019 Datacenter Core {architecture} {language}{suffix}",

            # Windows Server 2022
            "windows2022Standard": f"{prefix}Windows Server 2022 Standard GUI {architecture} {language}{suffix}",
            "windows2022StandardCore": f"{prefix}Windows Server 2022 Standard Core {architecture} {language}{suffix}",
            "windows2022Datacenter": f"{prefix}Windows Server 2022 Datacenter GUI {architecture} {language}{suffix}",
            "windows2022DatacenterCore": f"{prefix}Windows Server 2022 Datacenter Core {architecture} {language}{suffix}",

            # Windows Server 2025
            "windows2025Standard": f"{prefix}Windows Server 2025 Standard GUI {architecture} {language}{suffix}",
            "windows2025StandardCore": f"{prefix}Windows Server 2025 Standard Core {architecture} {language}{suffix}",
            "windows2025Datacenter": f"{prefix}Windows Server 2025 Datacenter GUI {architecture} {language}{suffix}",
            "windows2025DatacenterCore": f"{prefix}Windows Server 2025 Datacenter Core {architecture} {language}{suffix}",
        }

    def get_image_name(self, key: str) -> str:
        return self._names.get(key, key)
