def validate_loan_amount(value):
    if value is None:
        raise ValueError("Loan amount is reqquired")
    if value<0:
        raise ValueError("Loan amount cannot be neagtive")
    