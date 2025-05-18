from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence import auth, resources
from correspondence.db.deps import get_db_asession
from correspondence.deps import get_organization_by_slug
from correspondence.models import Organization, User

router = APIRouter()


@router.get("/")
async def root(
    state: auth.AuthState = Depends(auth.get_auth_state),
    asession: AsyncSession = Depends(get_db_asession),
) -> RedirectResponse:
    if state.user.is_authenticated:
        organization = await state.user.get_default_organization(asession)  # type:ignore
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no organization attached to the user",
            )

        return RedirectResponse(url=f"/organizations/{organization.slug}")

    return RedirectResponse(url="/login")


@router.get("/healthcheck")
async def healthcheck():
    return {"message": "ok"}


@router.get("/organizations/{organization_slug}")
async def organization_detail(
    request: Request,
    organization: Organization = Depends(get_organization_by_slug),
    authenticated_user: User = Depends(auth.get_authenticated_user),
):
    organization_resource = resources.OrganizationResource.from_model(organization)
    user_resource = resources.UserResource.from_model(authenticated_user)

    return request.app.templates.TemplateResponse(
        request=request,
        name="organization/detail.html",
        context={
            "organization": organization_resource,
            "authenticated_user": user_resource,
        },
    )


@router.post("/login")
async def login(
    form: auth.LoginForm,
    response: Response,
    asession: AsyncSession = Depends(get_db_asession),
):
    user = await auth.login(asession, form)
    token = auth.authenticate(user, response)

    return {"token": token}


@router.get("/admin")
async def admin(
    authenticated_user: User = Depends(auth.get_authenticated_user),
):
    return {"message": "ok"}


@router.get("/logout")
async def logout():
    return {"message": "ok"}


@router.get("/panic")
async def trigger_error():
    division_by_zero = 1 / 0
