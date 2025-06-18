"""Test data generation utilities."""

import random
import string
from typing import Any

from faker import Faker

fake = Faker()


class LDAPDataGenerator:
    """Generate realistic LDAP test data."""

    def __init__(self, seed: int | None = None):
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self.fake = Faker()
        self.used_uids = set()
        self.used_emails = set()
        self.used_employee_numbers = set()

    def generate_user(
        self,
        department: str | None = None,
        manager_dn: str | None = None,
        inactive: bool = False,
    ) -> dict[str, Any]:
        """Generate a realistic user entry."""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()

        # Ensure unique uid
        uid = self._generate_unique_uid(first_name, last_name)

        # Ensure unique email
        email = self._generate_unique_email(first_name, last_name)

        # Ensure unique employee number
        employee_number = self._generate_unique_employee_number()

        user = {
            "uid": uid,
            "cn": f"{first_name} {last_name}",
            "sn": last_name,
            "givenName": first_name,
            "displayName": f"{first_name} {last_name}",
            "mail": email,
            "userPassword": "{SSHA}password123",
            "uidNumber": str(random.randint(20000, 30000)),
            "gidNumber": str(random.randint(20000, 20010)),
            "homeDirectory": f"/home/{uid}",
            "loginShell": "/bin/bash" if not inactive else "/bin/false",
            "gecos": f"{first_name} {last_name}",
            "employeeNumber": employee_number,
            "employeeType": (
                "terminated"
                if inactive
                else random.choice(["full-time", "part-time", "contractor"])
            ),
            "telephoneNumber": self.fake.phone_number(),
            "mobile": self.fake.phone_number(),
            "roomNumber": f"{random.choice(['A', 'B', 'C'])}-{random.randint(100, 500)}",
        }

        if department:
            user["departmentNumber"] = department
            user["department"] = self._get_department_name(department)

        if manager_dn:
            user["manager"] = manager_dn

        # Add title based on department
        user["title"] = self._generate_title(department)

        # Add description
        user["description"] = f"{user['title']} in {user.get('department', 'Company')}"

        # Add random attributes for testing
        if random.random() > 0.5:
            user["carLicense"] = self.fake.license_plate()

        if random.random() > 0.3:
            user["preferredLanguage"] = random.choice(["en", "es", "fr", "de", "pt"])

        if inactive:
            user["accountStatus"] = "inactive"

        return user

    def generate_group(
        self, group_type: str = "generic", member_dns: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate a group entry."""
        group_types = {
            "department": [
                "Engineering",
                "Sales",
                "Marketing",
                "Finance",
                "HR",
                "Operations",
            ],
            "project": [
                "Project Alpha",
                "Project Beta",
                "Project Gamma",
                "Innovation Lab",
            ],
            "role": [
                "Administrators",
                "Developers",
                "Analysts",
                "Managers",
                "Directors",
            ],
            "location": ["Office NYC", "Office SF", "Office London", "Remote Workers"],
            "generic": [
                "All Staff",
                "Contractors",
                "Full Time Employees",
                "Part Time Staff",
            ],
        }

        if group_type not in group_types:
            group_type = "generic"

        name = random.choice(group_types[group_type])
        cn = name.lower().replace(" ", "-")

        return {
            "cn": cn,
            "description": f"{name} group",
            "member": member_dns or ["cn=admin,dc=example,dc=com"],
        }

    def generate_organizational_unit(self, ou_type: str = "generic") -> dict[str, Any]:
        """Generate an organizational unit."""
        ou_types = {
            "location": ["New York", "San Francisco", "London", "Tokyo", "Sydney"],
            "function": ["Engineering", "Sales", "Marketing", "Operations", "Support"],
            "project": ["ProjectA", "ProjectB", "Research", "Development"],
            "generic": ["Resources", "External", "Partners", "Temporary"],
        }

        if ou_type not in ou_types:
            ou_type = "generic"

        name = random.choice(ou_types[ou_type])

        return {"ou": name, "description": f"{name} organizational unit"}

    def generate_service_account(self, service_name: str) -> dict[str, Any]:
        """Generate a service account entry."""
        uid = f"svc-{service_name.lower()}"

        return {
            "uid": uid,
            "cn": f"{service_name} Service Account",
            "sn": "Service",
            "description": f"Service account for {service_name}",
            "userPassword": "{SSHA}" + self._generate_strong_password(),
        }

    def generate_bulk_users(
        self, count: int, department_distribution: dict[str, float] | None = None
    ) -> list[dict[str, Any]]:
        """Generate multiple users with realistic distribution."""
        if not department_distribution:
            department_distribution = {
                "ENG": 0.4,
                "SALES": 0.2,
                "MKT": 0.15,
                "OPS": 0.15,
                "HR": 0.1,
            }

        users = []

        # Calculate department counts
        dept_counts = {}
        remaining = count
        for dept, ratio in department_distribution.items():
            dept_count = int(count * ratio)
            dept_counts[dept] = dept_count
            remaining -= dept_count

        # Add remaining to largest department
        if remaining > 0:
            largest_dept = max(dept_counts, key=dept_counts.get)
            dept_counts[largest_dept] += remaining

        # Generate users per department
        for dept, dept_count in dept_counts.items():
            # Create some managers (10% of department)
            manager_count = max(1, dept_count // 10)

            managers = []
            for _ in range(manager_count):
                manager = self.generate_user(department=dept)
                manager["title"] = f"{manager['title']} Manager"
                users.append(manager)
                managers.append(
                    f"uid={manager['uid']},ou=People,dc=source,dc=example,dc=com"
                )

            # Create regular employees
            for _ in range(dept_count - manager_count):
                manager_dn = random.choice(managers) if managers else None
                user = self.generate_user(department=dept, manager_dn=manager_dn)
                users.append(user)

        # Add some inactive users (5% of total)
        inactive_count = max(1, count // 20)
        for _ in range(inactive_count):
            user = self.generate_user(inactive=True)
            users.append(user)

        return users

    def generate_organizational_structure(self) -> dict[str, Any]:
        """Generate a complete organizational structure."""
        structure = {
            "organizational_units": [],
            "groups": [],
            "users": [],
            "relationships": [],
        }

        # Create OUs
        base_ous = ["People", "Groups", "Applications", "Departments", "Projects"]
        for ou in base_ous:
            structure["organizational_units"].append(
                {"ou": ou, "description": f"{ou} container"}
            )

        # Create department OUs
        departments = ["Engineering", "Sales", "Marketing", "Operations", "HR"]
        for dept in departments:
            structure["organizational_units"].append(
                {
                    "ou": dept,
                    "parent": "ou=Departments",
                    "description": f"{dept} Department",
                }
            )

        # Create groups
        for dept in departments:
            dept_group = self.generate_group("department")
            dept_group["cn"] = dept.lower()
            structure["groups"].append(dept_group)

        # Create role groups
        for role in ["managers", "developers", "analysts", "administrators"]:
            role_group = self.generate_group("role")
            role_group["cn"] = role
            structure["groups"].append(role_group)

        return structure

    def _generate_unique_uid(self, first_name: str, last_name: str) -> str:
        """Generate a unique uid."""
        base_uid = f"{first_name.lower()}.{last_name.lower()}"
        uid = base_uid
        counter = 1

        while uid in self.used_uids:
            uid = f"{base_uid}{counter}"
            counter += 1

        self.used_uids.add(uid)
        return uid

    def _generate_unique_email(self, first_name: str, last_name: str) -> str:
        """Generate a unique email."""
        domain = random.choice(["example.com", "test.com", "demo.org"])
        base_email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
        email = base_email
        counter = 1

        while email in self.used_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@{domain}"
            counter += 1

        self.used_emails.add(email)
        return email

    def _generate_unique_employee_number(self) -> str:
        """Generate a unique employee number."""
        while True:
            emp_num = f"EMP{random.randint(10000, 99999)}"
            if emp_num not in self.used_employee_numbers:
                self.used_employee_numbers.add(emp_num)
                return emp_num

    def _generate_title(self, department: str | None) -> str:
        """Generate a job title based on department."""
        titles = {
            "ENG": [
                "Software Engineer",
                "Senior Software Engineer",
                "DevOps Engineer",
                "Data Engineer",
                "QA Engineer",
                "Engineering Manager",
            ],
            "SALES": [
                "Sales Representative",
                "Account Executive",
                "Sales Manager",
                "Business Development Representative",
                "Sales Director",
            ],
            "MKT": [
                "Marketing Specialist",
                "Content Manager",
                "Marketing Manager",
                "Brand Manager",
                "Digital Marketing Specialist",
            ],
            "OPS": [
                "Operations Manager",
                "Operations Analyst",
                "Supply Chain Manager",
                "Logistics Coordinator",
                "Operations Director",
            ],
            "HR": [
                "HR Specialist",
                "Recruiter",
                "HR Manager",
                "Talent Acquisition Specialist",
                "HR Business Partner",
            ],
        }

        if department and department in titles:
            return random.choice(titles[department])

        return random.choice(
            ["Specialist", "Analyst", "Manager", "Coordinator", "Associate"]
        )

    def _get_department_name(self, dept_code: str) -> str:
        """Get full department name from code."""
        dept_names = {
            "ENG": "Engineering",
            "SALES": "Sales",
            "MKT": "Marketing",
            "OPS": "Operations",
            "HR": "Human Resources",
            "FIN": "Finance",
            "LEGAL": "Legal",
        }
        return dept_names.get(dept_code, "General")

    def _generate_strong_password(self) -> str:
        """Generate a strong password."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(random.choice(chars) for _ in range(16))
