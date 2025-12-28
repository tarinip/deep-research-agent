# import os
# import yaml
# from typing import Dict, List, Any

# class ResearchTemplateLoader:
#     def __init__(self, base_path="plugins"):
#         # Ensures we have an absolute path to your plugins folder
#         self.base_path = os.path.abspath(os.path.join(os.getcwd(), base_path))

#     def get_domain_map(self) -> Dict[str, List[str]]:
#         """Scans folders to see what domains and templates exist."""
#         domain_map = {}
#         if not os.path.exists(self.base_path):
#             return {"general": ["standard_research"]}

#         # List only the top-level directories in /plugins as domains
#         for domain in os.listdir(self.base_path):
#             domain_path = os.path.join(self.base_path, domain)
#             if os.path.isdir(domain_path):
#                 templates = [
#                     f.replace('.yaml', '') 
#                     for f in os.listdir(domain_path) 
#                     if f.endswith('.yaml')
#                 ]
#                 if templates:
#                     domain_map[domain] = templates
#         return domain_map

#     def load_from_domain(self, domain: str, template: str, target: str) -> Dict[str, Any]:
#         """Loads a single YAML file and injects the target string."""
#         file_path = os.path.join(self.base_path, domain, f"{template}.yaml")
        
#         if not os.path.exists(file_path):
#             # Fallback check: if the specific template doesn't exist, try 'general'
#             print(f"⚠️ Template {template} not found in {domain}, trying 'general'...")
#             file_path = os.path.join(self.base_path, domain, "general.yaml")

#         if not os.path.exists(file_path):
#             raise FileNotFoundError(f"Could not find template '{template}' or 'general' in domain '{domain}'")

#         with open(file_path, 'r') as f:
#             data = yaml.safe_load(f)

#         # Replace all instances of {target} in the YAML with the actual entity (e.g., "Tokyo")
#         return self._inject_target(data, target)

#     def load_multiple_from_domain(self, domain: str, templates: list, target: str) -> Dict[str, Any]:
#         """Merges multiple templates into a single combined research plan."""
#         combined_objectives = []
#         final_settings = {"depth": "intermediate"}

#         for t_name in templates:
#             try:
#                 # This calls the method we just defined above
#                 plan = self.load_from_domain(domain, t_name, target)
                
#                 if "objectives" in plan:
#                     combined_objectives.extend(plan["objectives"])
                
#                 # If any selected template requires 'deep' depth, upgrade the whole mission
#                 if plan.get("settings", {}).get("depth") == "deep":
#                     final_settings["depth"] = "deep"
#             except Exception as e:
#                 print(f"⚠️ Error loading template '{t_name}': {e}")

#         return {
#             "objectives": combined_objectives,
#             "settings": final_settings
#         }

#     def _inject_target(self, data: Any, target: str) -> Any:
#         """Recursively replaces '{target}' placeholders with the actual target name."""
#         if isinstance(data, dict):
#             return {k: self._inject_target(v, target) for k, v in data.items()}
#         elif isinstance(data, list):
#             return [self._inject_target(i, target) for i in data]
#         elif isinstance(data, str):
#             return data.replace("{target}", target)
#         return data
import os
import yaml
from typing import Dict, List, Any

class ResearchTemplateLoader:
    def __init__(self, base_path="plugins"):
        # Absolute pathing prevents "File Not Found" errors in different environments
        self.base_path = os.path.abspath(os.path.join(os.getcwd(), base_path))
    def _inject_target(self, data: Any, target: str) -> Any:
        """
        Recursively walks through the template (dict, list, or str) 
        and replaces {target} with the actual topic.
        """
        if isinstance(data, str):
            return data.replace("{target}", target)
        elif isinstance(data, list):
            return [self._inject_target(item, target) for item in data]
        elif isinstance(data, dict):
            return {k: self._inject_target(v, target) for k, v in data.items()}
        return data
    
    # ... [get_domain_map and load_from_domain remain same] ...
    def load_from_domain(self, domain: str, template: str, target: str) -> Dict[str, Any]:
        """Loads a single YAML file and injects the target string."""
        file_path = os.path.join(self.base_path, domain, f"{template}.yaml")
        
        if not os.path.exists(file_path):
            # Fallback check: if the specific template doesn't exist, try 'general'
            print(f"⚠️ Template {template} not found in {domain}, trying 'general'...")
            file_path = os.path.join(self.base_path, domain, "general.yaml")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find template '{template}' or 'general' in domain '{domain}'")

        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Replace all instances of {target} in the YAML with the actual entity (e.g., "Tokyo")
        return self._inject_target(data, target)
    def load_multiple_from_domain(self, domain: str, templates: list, target: str) -> Dict[str, Any]:
        """Merges multiple templates into a single combined research plan."""
        combined_objectives = []
        
        # Default settings - we use 'standard' but will upgrade if any template asks for it
        final_settings = {"depth": "standard"}

        for t_name in templates:
            try:
                plan = self.load_from_domain(domain, t_name, target)
                
                # Merge Objectives: Combine all tasks into one master list
                if "objectives" in plan:
                    combined_objectives.extend(plan["objectives"])
                
                # Merge Settings: Implement "Highest Priority Wins"
                # If ANY template is 'deep', the whole mission is 'deep'.
                template_depth = plan.get("settings", {}).get("depth", "standard")
                if template_depth == "deep":
                    final_settings["depth"] = "deep"
                    
            except Exception as e:
                print(f"⚠️ Error loading template '{t_name}': {e}")

        return {
            "objectives": combined_objectives,
            "settings": final_settings
        }