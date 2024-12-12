from weather_forecast import TireType, AlertType


class ChatMessages:
    """
    The main idea of the class is to list
    all the messages that the bot will send to the user.
    The class can be extended with messages for other language.
    """

    def settings_start(self):
        return "👋 Hello!\n\n" f"{self.settings_location()}"

    def settings_start_configured_chat(self, place_name: str, tire_type: int):
        return "👋 Hello!\n\n" f"{self.settings_overview(place_name, tire_type)}"

    def settings_overview(self, place_name: str, tire_type: int):
        return (
            f"{self.settings_location_set(place_name)}\n\n"
            f"{self.settings_tire_type_set(tire_type)}\n\n"
            "⚙️ You can change your settings at any time."
        )

    def settings_overview_not_configured_chat(self):
        return "👀 Settings are not configured yet"

    def settings_configure_button(self):
        return "Configure settings"

    def settings_change_settings_keep_current(self):
        return "👌 Current settings are kept"

    def settings_location(self):
        return (
            "Please, select the way how you want to set your location:\n"
            "- 📍 Coordinates - latitude and longitude\n"
            "- 🏠 Place - location name"
        )

    def settings_location_coordinates(self):
        return (
            "📍 Enter the the coordinates of your location\n"
            "Accepted formats examples:\n"
            "- DMS: 41°24'12.2\"N 2°10'26.5\"E\n"
            "- Decimal: 41.4023,2.1745 or 41.4023 2.1745"
        )

    def settings_location_coordinates_invalid(self):
        return "🚫 Invalid coordinates, please, try again"

    def settings_location_place(self):
        return "🏠 Enter the name of a location"

    def settings_location_place_not_found(self):
        return "🔎 The settlement is not found, please, try again"

    def settings_location_set(self, place_name: str):
        return "🌐 Your location is:\n" f"{place_name}."

    def settings_location_confirmation(self, place_name: str):
        return f"{self.settings_location_set(place_name)}\n\n" "Is it correct?"

    def format_tire_type(self, tire_type: int):
        return "❄️ winter" if tire_type == TireType.Winter else "☀️ summer"

    def settings_tire_type_confirmation(self, avg_temperature: float, tire_type: int):
        return (
            f"🌡️ The average temperature in your location is {avg_temperature:.1f}°C for tomorrow.\n\n"
            f"🛞 Are you currently using {self.format_tire_type(tire_type)} tires?"
        )

    def settings_tire_type_set(self, tire_type: int):
        return (
            f"🛞 Your tire type is {self.format_tire_type(tire_type)}.\n\n"
            "📲 You will receive a message when the weather changes and it's time to schedule changing your tires."
        )

    def format_alert_type(self, alert_type: int):
        return (
            "from ❄️ winter tires to ☀️ summer"
            if alert_type == AlertType.WinterToSummer
            else "from ☀️ summer tires to winter"
        )

    def alert_change_tire_type(
        self,
        alert_type: int,
        alert_count: int,
        avg_temperature: float | None = None,
    ):
        if alert_count == 0:
            return (
                "👋 Hello!\n\n"
                f"🌡️ According weather forecast the average temperature is {avg_temperature:.1f}°C for next week.\n\n"
                f"🚗 It's a good time to schedule an appointment to change {self.format_alert_type(alert_type)}."
            )

        return (
            "👋 Hello again!\n\n"
            f"🚗 You asked to remind you to schedule an appointment to change {self.format_alert_type(alert_type)}."
        )

    def alert_notify_stop_button(self):
        return "Do not notify me again"

    def alert_notify_again_button(self):
        return "Notify me later again"

    def alert_notify_stop_confirm(self):
        return "👌 Confirmed "

    def alert_notify_again_confirm(self):
        return "✅ Confirmed"
