from models.plaid_access_model import PlaidAccess


def add_new_plaid_access(plaid_access_details: PlaidAccess):
    plaid_access = PlaidAccess.get_by_user_and_institution(plaid_access_details.user_id,
                                                           plaid_access_details.institution_id)
    if plaid_access:
        return
    plaid_access_details.save()


def get_plaid_access_token(item_id: str) -> PlaidAccess:
    return PlaidAccess.get_by_item_id(item_id)
