import os
import yaml

class ResearchTemplateLoader:
    def __init__(self, base_path="plugins"):
        self.base_path = os.path.join(os.getcwd(), base_path)

    def get_domain_map(self):
        """Scans folders to see what domains and templates exist."""
        domain_map = {}
        if not os.path.exists(self.base_path):
            return {"general": ["standard_research"]}

        for root, dirs, files in os.walk(self.base_path):
            for domain in dirs:
                domain_path = os.path.join(root, domain)
                templates = [f.replace('.yaml', '') for f in os.listdir(domain_path) if f.endswith('.yaml')]
                if templates:
                    domain_map[domain] = templates
        return domain_map

    # THIS IS THE FUNCTION YOUR SCOPING.PY IS LOOKING FOR
    def load_from_domain(self, domain, template, target): # <--- MATCH THESE NAMES
        file_path = os.path.join(self.base_path, domain, f"{template}.yaml")
        
        # Fallback to general.yaml if the specific one is missing
        if not os.path.exists(file_path):
            file_path = os.path.join(self.base_path, domain, "general.yaml")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Could not find template '{template}' or 'general' in folder '{domain}'")
            
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)

        config['current_target'] = target
        config['active_domain'] = domain
        return config