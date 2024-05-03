from whylabs_toolkit.monitor.diagnoser.recommendation.recommended_change import RecommendedChange


class ManualChange(RecommendedChange):
    name = "manual_change"
    summary = "Make a manual change to the analyzer to address {condition}: {summary}"
    required_info = ["condition"]
    manual = True

    def summarize(self) -> str:
        condition = self.info.get("condition", "") if self.info else ""
        if condition == "narrow_threshold_band":
            # percent diff of 0 would be bad... need to add info to differentiate
            return "Move columns to a new analyzer that uses absolute diff, percent diff or fixed thresholds"
        return super().summarize()
