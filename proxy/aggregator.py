from models import Employee, SourceIds

def merge_employees(
    atlas: list[Employee],
    beacon: list[Employee],
    cobalt: list[Employee],
) -> list[Employee]:

    # Índices por email normalizado para cada provider
    atlas_by_email  = {emp.email: emp for emp in atlas}
    beacon_by_email = {emp.email: emp for emp in beacon}
    cobalt_by_email = {emp.email: emp for emp in cobalt}

    all_emails = set(atlas_by_email) | set(beacon_by_email) | set(cobalt_by_email)

    return [
        _merge_one(
            email,
            atlas_by_email.get(email),
            beacon_by_email.get(email),
            cobalt_by_email.get(email),
        )
        for email in all_emails
    ]


def _merge_one(
    email: str,
    atlas: Employee | None,
    beacon: Employee | None,
    cobalt: Employee | None,
) -> Employee:
    name_source    = atlas or cobalt or beacon
    dept_source    = atlas or beacon or cobalt
    salary_source  = cobalt or atlas or beacon
    status_source  = beacon or atlas or cobalt
    date_source    = atlas or cobalt or beacon
    title_source   = cobalt or atlas or beacon
    primary        = atlas or beacon or cobalt

    return Employee(
        id=primary.id,
        source_ids=SourceIds(
            atlas=atlas.source_ids.atlas   if atlas  else None,
            beacon=beacon.source_ids.beacon if beacon else None,
            cobalt=cobalt.source_ids.cobalt if cobalt else None,
        ),
        first_name=name_source.first_name,
        last_name=name_source.last_name,
        email=email,
        job_title=title_source.job_title,
        department=dept_source.department,
        status=status_source.status,
        annual_salary=salary_source.annual_salary,
        currency=primary.currency,
        hire_date=date_source.hire_date,
        source="merged" if sum([atlas is not None, beacon is not None, cobalt is not None]) > 1 else primary.source,
    )