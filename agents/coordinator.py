# agents/coordinator.py

from typing import Dict, Optional, List
from agents.data_agent import get_phone_data, format_phone_specs
from agents.review_agent import generate_review, ReviewGenerator, PhoneSpecs
import json


class PhoneAnalysisCoordinator:
    """
    coordinator that manages multiple agents for comprehensive phone analysis.
    Provides both structured data and natural language reviews.
    """

    def __init__(self):
        self.review_generator = ReviewGenerator()

    def get_phone_comparison(self, phone_names: List[str]) -> Dict:
        """
        Compare multiple phones side by side.
        """
        comparisons = {}
        phone_specs = []

        for phone_name in phone_names:
            phone_data = get_phone_data(phone_name)
            if "error" not in phone_data:
                specs = self.review_generator.create_phone_specs_object(phone_data)
                phone_specs.append(specs)
                comparisons[phone_name] = {"specs": specs, "data": phone_data}

        if len(phone_specs) < 2:
            return {"error": "Need at least 2 valid phones for comparison"}

        # Generate comparison analysis
        comparison_analysis = self._generate_comparison_analysis(phone_specs)

        return {
            "phones": comparisons,
            "comparison_analysis": comparison_analysis,
            "winner_analysis": self._determine_winners(phone_specs),
        }

    def _generate_comparison_analysis(self, phone_specs: List[PhoneSpecs]) -> Dict:
        """Generate detailed comparison analysis"""
        analysis = {
            "performance": self._compare_performance(phone_specs),
            "camera": self._compare_cameras(phone_specs),
            "battery": self._compare_battery(phone_specs),
            "display": self._compare_display(phone_specs),
            "value": self._compare_value(phone_specs),
        }
        return analysis

    def _compare_performance(self, phones: List[PhoneSpecs]) -> str:
        """Compare performance across phones"""
        flagship_phones = [p for p in phones if p.price_tier == "flagship"]
        if flagship_phones:
            best_performer = max(
                flagship_phones,
                key=lambda x: max(x.ram_variants) if x.ram_variants else 0,
            )
        else:
            best_performer = max(
                phones, key=lambda x: max(x.ram_variants) if x.ram_variants else 0
            )

        return f"In terms of performance, the {best_performer.name} leads with its {best_performer.chipset} processor and up to {max(best_performer.ram_variants) if best_performer.ram_variants else 'N/A'}GB RAM configuration."

    def _compare_cameras(self, phones: List[PhoneSpecs]) -> str:
        """Compare camera capabilities"""
        best_camera = max(phones, key=lambda x: x.main_camera_mp)
        return f"For photography, the {best_camera.name} takes the lead with its {best_camera.main_camera_mp}MP main camera sensor."

    def _compare_battery(self, phones: List[PhoneSpecs]) -> str:
        """Compare battery life"""
        best_battery = max(phones, key=lambda x: x.battery_capacity)
        return f"Battery life is dominated by the {best_battery.name} with its {best_battery.battery_capacity}mAh battery."

    def _compare_display(self, phones: List[PhoneSpecs]) -> str:
        """Compare display quality"""
        largest_display = max(phones, key=lambda x: x.display_size)
        return f"The {largest_display.name} offers the most immersive viewing experience with its {largest_display.display_size}-inch display."

    def _compare_value(self, phones: List[PhoneSpecs]) -> str:
        """Compare value propositions"""
        mid_range_phones = [
            p for p in phones if p.price_tier in ["mid_range", "upper_mid"]
        ]
        if mid_range_phones:
            best_value = max(
                mid_range_phones,
                key=lambda x: x.main_camera_mp + x.battery_capacity / 50,
            )
            return f"For value-conscious buyers, the {best_value.name} offers the best balance of features and price."
        else:
            return "All compared phones are in the premium segment, offering flagship features at premium prices."

    def _determine_winners(self, phones: List[PhoneSpecs]) -> Dict:
        """Determine category winners"""
        return {
            "best_overall": max(
                phones, key=lambda x: self._calculate_overall_score(x)
            ).name,
            "best_camera": max(phones, key=lambda x: x.main_camera_mp).name,
            "best_battery": max(phones, key=lambda x: x.battery_capacity).name,
            "best_performance": max(
                phones, key=lambda x: max(x.ram_variants) if x.ram_variants else 0
            ).name,
            "best_value": min(
                phones, key=lambda x: 1 if x.price_tier == "flagship" else 0
            ).name,
        }

    def _calculate_overall_score(self, phone: PhoneSpecs) -> float:
        """Calculate overall phone score"""
        score = 0

        # Performance score (30%)
        max_ram = max(phone.ram_variants) if phone.ram_variants else 8
        score += (max_ram / 16) * 30

        # Camera score (25%)
        score += (phone.main_camera_mp / 200) * 25

        # Battery score (25%)
        score += (phone.battery_capacity / 5000) * 25

        # Display score (10%)
        score += (phone.display_size / 7.0) * 10

        # Features bonus (10%)
        feature_bonus = len(phone.special_features) * 2
        score += min(feature_bonus, 10)

        return score

    def generate_phone_summary(self, phone_name: str) -> Dict:
        """
        phone summary with comprehensive analysis.
        """
        phone_data = get_phone_data(phone_name)

        if "error" in phone_data:
            return {
                "error": phone_data["error"],
                "review": None,
                "formatted_specs": None,
                "analysis": None,
            }

        # Generate comprehensive review
        review = generate_review(phone_name)

        # Format basic specs
        formatted_specs = format_phone_specs(phone_data)

        # Generate detailed analysis
        specs_obj = self.review_generator.create_phone_specs_object(phone_data)
        analysis = self._generate_detailed_analysis(specs_obj)

        return {
            "phone_name": phone_name,
            "formatted_specs": formatted_specs,
            "review": review,
            "analysis": analysis,
            "specs_object": specs_obj.__dict__,  # For API responses
        }

    def _generate_detailed_analysis(self, specs: PhoneSpecs) -> Dict:
        """Generate detailed technical analysis"""
        return {
            "performance_tier": self.review_generator.analyzer.determine_chipset_tier(
                specs.chipset
            ),
            "price_tier": specs.price_tier,
            "key_strengths": self._identify_strengths(specs),
            "potential_weaknesses": self._identify_weaknesses(specs),
            "target_audience": self._identify_target_audience(specs),
            "overall_score": round(self._calculate_overall_score(specs), 1),
        }

    def _identify_strengths(self, specs: PhoneSpecs) -> List[str]:
        """Identify phone's key strengths"""
        strengths = []

        if specs.battery_capacity >= 5000:
            strengths.append("Excellent battery life")

        if specs.main_camera_mp >= 100:
            strengths.append("High-resolution camera")

        if "Optical Image Stabilization" in specs.special_features:
            strengths.append("Advanced camera stabilization")

        if max(specs.ram_variants) >= 12 if specs.ram_variants else False:
            strengths.append("Ample RAM for multitasking")

        if specs.display_size >= 6.7:
            strengths.append("Large, immersive display")

        if "5G Connectivity" in specs.special_features:
            strengths.append("Future-ready connectivity")

        return strengths

    def _identify_weaknesses(self, specs: PhoneSpecs) -> List[str]:
        """Identify potential weaknesses"""
        weaknesses = []

        if specs.battery_capacity < 4000:
            weaknesses.append("Limited battery capacity")

        if max(specs.ram_variants) < 8 if specs.ram_variants else True:
            weaknesses.append("Limited RAM for heavy multitasking")

        if specs.main_camera_mp < 50:
            weaknesses.append("Basic camera system")

        if specs.price_tier == "flagship" and specs.main_camera_mp < 100:
            weaknesses.append("Camera could be better for flagship price")

        return weaknesses

    def _identify_target_audience(self, specs: PhoneSpecs) -> str:
        """Identify target audience for the phone"""
        if specs.price_tier == "flagship":
            return "Power users, photography enthusiasts, and those who want the absolute best Samsung has to offer"
        elif specs.price_tier == "premium":
            return "Users who want flagship features without the ultra-premium price"
        elif specs.price_tier == "upper_mid":
            return "Mainstream users who want good performance and features at a reasonable price"
        else:
            return "Budget-conscious users who want a reliable Samsung device with decent features"


# Main coordination function
def generate_phone_summary(phone_name: str) -> Dict:
    """
    Generate comprehensive phone analysis using multi-agent system.
    """
    coordinator = PhoneAnalysisCoordinator()
    return coordinator.generate_phone_summary(phone_name)


def compare_phones(phone_names: List[str]) -> Dict:
    """
    Compare multiple phones using analysis.
    """
    coordinator = PhoneAnalysisCoordinator()
    return coordinator.get_phone_comparison(phone_names)
