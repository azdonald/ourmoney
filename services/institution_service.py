from models.instituition_model import Institution


def add_institution(new_institution: Institution) -> Institution:
    institution = Institution.get_by_name(new_institution.name)
    if institution:
        return institution
    new_institution.save()
    return new_institution


def get_institution_and_accounts(user_id: int):
    return Institution.get_with_accounts(user_id)
