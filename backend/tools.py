# backend/tools.py

def calculate_speed_fine(posted_limit: float, actual_speed: float) -> float:
    """
    Calculates the fine amount for overspeeding violations.
    Takes the posted speed sign limit and the actual speed of the vehicle.
    """
    if actual_speed <= posted_limit:
        return 0.0

    excess_speed = actual_speed - posted_limit
    # Law states: ₹100 penalty for every 1 km/h over the limit
    fine = excess_speed * 100.0
    return float(fine)


def mock_toll_wallet_deduction(vehicle_id: str, total_fine_amount: float) -> str:
    """
    Simulates a digital wallet or FASTag transaction deduction at the toll booth scanner.
    Takes a vehicle identification number string and the total fine amount float.
    """
    if total_fine_amount <= 0:
        return f"Vehicle {vehicle_id} cleared. No outstanding fine deductions needed."

    # Simulating a transaction confirmation event
    return f"SUCCESS: Deducted ₹{total_fine_amount:.2f} from FASTag Wallet linked to Vehicle {vehicle_id}."
