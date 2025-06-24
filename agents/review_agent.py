# agents/enhanced_review_agent.py

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from agents.data_agent import get_phone_data


@dataclass
class PhoneSpecs:
    """Structured phone specifications for better analysis"""

    name: str
    display_size: float
    resolution: str
    chipset: str
    ram_variants: List[int]
    storage_variants: List[int]
    main_camera_mp: int
    battery_capacity: int
    release_year: int
    price_tier: str
    os_version: str
    build_quality: str
    special_features: List[str]


class SpecAnalyzer:
    """Analyzes phone specifications and provides insights"""

    CHIPSET_TIERS = {
        "flagship": [
            "Snapdragon 8 Elite",
            "Snapdragon 8 Gen 3",
            "Snapdragon 8 Gen 2",
            "Exynos 2400",
        ],
        "upper_mid": ["Snapdragon 7 Gen", "Exynos 1580", "Exynos 1480"],
        "mid_range": ["Snapdragon 6 Gen", "Exynos 1380", "Exynos 1280"],
        "budget": ["Snapdragon 4 Gen", "Exynos 850"],
    }

    PRICE_TIERS = {
        "flagship": ["S25 Ultra", "S24 Ultra", "S23 Ultra", "S22 Ultra", "S21 Ultra"],
        "premium": ["S25 Edge", "S25", "S24", "S23"],
        "upper_mid": ["S24 FE", "A56", "A55"],
        "mid_range": ["A36", "A35", "A26"],
    }

    @staticmethod
    def parse_display_size(display_str: str) -> float:
        """Extract display size from string like '6.7 inches'"""
        match = re.search(r"(\d+\.\d+)", display_str)
        return float(match.group(1)) if match else 0.0

    @staticmethod
    def parse_camera_mp(camera_str: str) -> int:
        """Extract main camera MP from string"""
        match = re.search(r"(\d+)\s*MP", camera_str)
        return int(match.group(1)) if match else 0

    @staticmethod
    def parse_battery_capacity(battery_str: str) -> int:
        """Extract battery capacity from string like '5000 mAh'"""
        match = re.search(r"(\d+)", battery_str)
        return int(match.group(1)) if match else 0

    @staticmethod
    def parse_ram_storage(
        ram_str: str, storage_str: str
    ) -> Tuple[List[int], List[int]]:
        """Parse RAM and storage variants"""
        ram_variants = []
        storage_variants = []

        # Extract all numbers followed by 'GB'
        ram_matches = re.findall(r"(\d+)GB", ram_str)
        storage_matches = re.findall(r"(\d+)GB", storage_str)

        ram_variants = list(set(int(x) for x in ram_matches))
        storage_variants = list(set(int(x) for x in storage_matches))

        return sorted(ram_variants), sorted(storage_variants)

    @staticmethod
    def determine_price_tier(phone_name: str) -> str:
        """Determine price tier based on phone name"""
        name_upper = phone_name.upper()

        for tier, models in SpecAnalyzer.PRICE_TIERS.items():
            for model in models:
                if model.upper() in name_upper:
                    return tier
        return "mid_range"

    @staticmethod
    def determine_chipset_tier(chipset: str) -> str:
        """Determine chipset performance tier"""
        for tier, chips in SpecAnalyzer.CHIPSET_TIERS.items():
            for chip in chips:
                if chip in chipset:
                    return tier
        return "mid_range"

    @staticmethod
    def extract_special_features(phone_data: dict) -> List[str]:
        """Extract special features from phone data"""
        features = []
        specs = phone_data.get("structured", {})

        # Check for OIS
        if "OIS" in specs.get("Camera", ""):
            features.append("Optical Image Stabilization")

        # Check for high refresh rate
        if "120Hz" in str(specs.get("Display", "")):
            features.append("120Hz Display")

        # Check for fast charging
        battery_info = specs.get("Battery", "")
        if "fast" in battery_info.lower() or "wireless" in battery_info.lower():
            features.append("Fast Charging")

        # Check for 5G
        if "5G" in specs.get("Network", ""):
            features.append("5G Connectivity")

        # Check for S Pen (Ultra models)
        if "Ultra" in specs.get("Name", ""):
            features.append("S Pen Support")

        return features


class ReviewGenerator:
    """Generates comprehensive phone reviews"""

    def __init__(self):
        self.analyzer = SpecAnalyzer()

    def create_phone_specs_object(self, phone_data: dict) -> PhoneSpecs:
        """Convert raw phone data to structured PhoneSpecs object"""
        specs = phone_data.get("structured", {})

        ram_variants, storage_variants = self.analyzer.parse_ram_storage(
            specs.get("RAM", ""), specs.get("Storage", "")
        )

        return PhoneSpecs(
            name=specs.get("Name", ""),
            display_size=self.analyzer.parse_display_size(specs.get("Display", "")),
            resolution=specs.get("Resolution", ""),
            chipset=specs.get("Chipset", ""),
            ram_variants=ram_variants,
            storage_variants=storage_variants,
            main_camera_mp=self.analyzer.parse_camera_mp(specs.get("Camera", "")),
            battery_capacity=self.analyzer.parse_battery_capacity(
                specs.get("Battery", "")
            ),
            release_year=self._extract_year(specs.get("Release Date", "")),
            price_tier=self.analyzer.determine_price_tier(specs.get("Name", "")),
            os_version=specs.get("OS", ""),
            build_quality=self._assess_build_quality(specs.get("Name", "")),
            special_features=self.analyzer.extract_special_features(phone_data),
        )

    def _extract_year(self, release_date: str) -> int:
        """Extract year from release date"""
        match = re.search(r"(\d{4})", release_date)
        return int(match.group(1)) if match else 2024

    def _assess_build_quality(self, name: str) -> str:
        """Assess build quality based on phone tier"""
        if any(x in name.upper() for x in ["ULTRA", "S25", "S24", "S23"]):
            return "Premium"
        elif any(x in name.upper() for x in ["A56", "A55", "FE"]):
            return "Good"
        else:
            return "Standard"

    def generate_performance_analysis(self, specs: PhoneSpecs) -> str:
        """Generate detailed performance analysis"""
        chipset_tier = self.analyzer.determine_chipset_tier(specs.chipset)

        performance_map = {
            "flagship": "delivers exceptional performance that handles any task with ease. Whether you're gaming, multitasking, or running demanding applications, this phone won't skip a beat. The latest flagship processor ensures smooth performance for years to come.",
            "upper_mid": "offers excellent performance for most users. It handles daily tasks, moderate gaming, and multitasking very well. You'll experience smooth performance in most scenarios, with only the most demanding games potentially showing minor limitations.",
            "mid_range": "provides solid performance for everyday use. It handles basic tasks, light gaming, and standard apps without issues. While it may not be the fastest for heavy multitasking or intensive gaming, it's perfectly adequate for most users.",
            "budget": "offers decent performance for basic usage. It's suitable for calling, texting, social media, and light apps, but may struggle with heavy multitasking or demanding games.",
        }

        base_performance = performance_map.get(
            chipset_tier, performance_map["mid_range"]
        )

        # Add RAM analysis
        max_ram = max(specs.ram_variants) if specs.ram_variants else 8
        if max_ram >= 12:
            ram_analysis = " The generous RAM ensures excellent multitasking capabilities and keeps apps running smoothly in the background."
        elif max_ram >= 8:
            ram_analysis = " With adequate RAM, you can run multiple apps simultaneously without significant slowdowns."
        else:
            ram_analysis = " The RAM is sufficient for basic multitasking, though heavy users might experience occasional app reloads."

        return f"The {specs.name} {base_performance}{ram_analysis}"

    def generate_camera_analysis(self, specs: PhoneSpecs) -> str:
        """Generate detailed camera analysis"""
        camera_quality = {
            200: "flagship-level",
            108: "excellent",
            50: "very good",
            48: "good",
            32: "decent",
            16: "basic",
        }

        quality = "good"
        for mp_threshold, quality_desc in sorted(camera_quality.items(), reverse=True):
            if specs.main_camera_mp >= mp_threshold:
                quality = quality_desc
                break

        analysis = f"The camera system features a {specs.main_camera_mp}MP main sensor that delivers {quality} photo quality. "

        if specs.main_camera_mp >= 100:
            analysis += "The high-resolution sensor captures incredibly detailed photos with excellent dynamic range. You'll get professional-quality results in various lighting conditions."
        elif specs.main_camera_mp >= 50:
            analysis += "The sensor captures sharp, detailed photos with good color reproduction. It performs well in daylight and decent in low-light conditions."
        else:
            analysis += "The camera is suitable for everyday photography, capturing decent photos for social media and memories."

        if "Optical Image Stabilization" in specs.special_features:
            analysis += " The optical image stabilization helps reduce blur in photos and provides smoother video recording."

        return analysis

    def generate_battery_analysis(self, specs: PhoneSpecs) -> str:
        """Generate battery life analysis"""
        if specs.battery_capacity >= 5000:
            battery_life = "excellent"
            usage_desc = "easily last a full day of heavy usage, and moderate users can expect up to two days"
        elif specs.battery_capacity >= 4500:
            battery_life = "very good"
            usage_desc = "comfortably last a full day of moderate to heavy usage"
        elif specs.battery_capacity >= 4000:
            battery_life = "good"
            usage_desc = "get you through a full day of moderate usage"
        else:
            battery_life = "adequate"
            usage_desc = "handle moderate usage throughout the day, though heavy users might need a midday charge"

        analysis = f"With a {specs.battery_capacity}mAh battery, the {specs.name} offers {battery_life} battery life. You can expect it to {usage_desc}."

        if "Fast Charging" in specs.special_features:
            analysis += " Fast charging support means you can quickly top up the battery when needed."

        return analysis

    def generate_display_analysis(self, specs: PhoneSpecs) -> str:
        """Generate display analysis"""
        size_desc = ""
        if specs.display_size >= 6.8:
            size_desc = "large, immersive"
        elif specs.display_size >= 6.5:
            size_desc = "generous"
        elif specs.display_size >= 6.0:
            size_desc = "comfortable"
        else:
            size_desc = "compact"

        analysis = f"The {specs.display_size}-inch display provides a {size_desc} viewing experience. "

        if "1440" in specs.resolution:
            analysis += "The high resolution ensures crisp, sharp text and vibrant images, making it excellent for media consumption and productivity."
        elif "1080" in specs.resolution:
            analysis += "The Full HD+ resolution delivers sharp visuals and good color reproduction for everyday use."
        else:
            analysis += (
                "The display quality is adequate for basic tasks and media viewing."
            )

        if "120Hz" in specs.special_features:
            analysis += " The 120Hz refresh rate provides incredibly smooth scrolling and responsive touch interactions."

        return analysis

    def generate_value_proposition(self, specs: PhoneSpecs) -> str:
        """Generate value proposition analysis"""
        value_props = {
            "flagship": f"The {specs.name} is a premium flagship device that justifies its high price with cutting-edge features, exceptional performance, and build quality. It's ideal for users who want the absolute best and are willing to pay for it.",
            "premium": f"The {specs.name} offers flagship-level features at a more accessible price point. It provides excellent value for users who want premium features without the ultra-premium price tag.",
            "upper_mid": f"The {specs.name} strikes an excellent balance between features and price. It offers many premium features at a reasonable cost, making it a great choice for most users.",
            "mid_range": f"The {specs.name} provides solid value for money, offering good performance and features at an affordable price. It's perfect for users who want a reliable Samsung phone without breaking the bank.",
        }

        return value_props.get(specs.price_tier, value_props["mid_range"])

    def generate_comprehensive_review(self, phone_name: str) -> str:
        """Generate a comprehensive, professional phone review"""
        phone_data = get_phone_data(phone_name)

        if "error" in phone_data:
            return f"Unable to generate review: {phone_data['error']}"

        specs = self.create_phone_specs_object(phone_data)

        # Generate review sections
        intro = f"# {specs.name} Review\n\n"

        overview = f"The {specs.name} is Samsung's {specs.release_year} {specs.price_tier.replace('_', ' ')} offering that aims to deliver a compelling smartphone experience. "

        if specs.special_features:
            overview += (
                f"Key highlights include {', '.join(specs.special_features[:-1])}"
            )
            if len(specs.special_features) > 1:
                overview += f" and {specs.special_features[-1]}."
            else:
                overview += "."

        # Detailed analysis sections
        performance_section = (
            f"\n\n## Performance\n{self.generate_performance_analysis(specs)}"
        )
        camera_section = f"\n\n## Camera\n{self.generate_camera_analysis(specs)}"
        battery_section = (
            f"\n\n## Battery Life\n{self.generate_battery_analysis(specs)}"
        )
        display_section = f"\n\n## Display\n{self.generate_display_analysis(specs)}"

        # Storage and variants
        storage_section = f"\n\n## Storage & Memory\n"
        if specs.storage_variants and specs.ram_variants:
            storage_section += f"The {specs.name} comes in multiple configurations: "
            configs = []
            for storage in specs.storage_variants:
                for ram in specs.ram_variants:
                    configs.append(f"{storage}GB storage with {ram}GB RAM")
            storage_section += ", ".join(configs[:3])  # Limit to first 3 configs
            if len(configs) > 3:
                storage_section += f" and {len(configs) - 3} more variants"
            storage_section += ". This variety ensures there's an option for different usage needs and budgets."

        # Value proposition
        value_section = (
            f"\n\n## Value Proposition\n{self.generate_value_proposition(specs)}"
        )

        # Conclusion
        conclusion = f"\n\n## Conclusion\n"
        conclusion += f"The {specs.name} is a {specs.build_quality.lower()} smartphone that delivers "

        strengths = []
        if specs.battery_capacity >= 5000:
            strengths.append("excellent battery life")
        if specs.main_camera_mp >= 50:
            strengths.append("solid camera performance")
        if "Optical Image Stabilization" in specs.special_features:
            strengths.append("advanced camera features")
        if specs.display_size >= 6.5:
            strengths.append("immersive display")

        if strengths:
            conclusion += f"{', '.join(strengths[:-1])}"
            if len(strengths) > 1:
                conclusion += f" and {strengths[-1]}."
            else:
                conclusion += "."

        conclusion += f" It's particularly well-suited for users seeking a reliable Samsung device in the {specs.price_tier.replace('_', ' ')} segment."

        # Combine all sections
        full_review = (
            intro
            + overview
            + performance_section
            + camera_section
            + battery_section
            + display_section
            + storage_section
            + value_section
            + conclusion
        )

        return full_review


# Enhanced main function
def generate_review(phone_name: str) -> str:
    """
    Generate a comprehensive, professional phone review.
    This replaces the basic review_agent.py functionality.
    """
    generator = ReviewGenerator()
    return generator.generate_comprehensive_review(phone_name)
