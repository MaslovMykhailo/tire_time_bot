class TireType:
    Winter = 0
    Summer = 1


class AlertType:
    WinterToSummer = 0
    SummerToWinter = 1


def get_tire_type_by_avg_temperature(avg_temperature: float) -> int:
    return TireType.Winter if avg_temperature < 7 else TireType.Summer


def get_opposite_tire_type(tire_type: int) -> int:
    return TireType.Summer if tire_type == TireType.Winter else TireType.Winter
