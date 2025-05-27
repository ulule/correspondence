from typing import Annotated

from fastapi import (APIRouter, Depends, Form, HTTPException, Request,
                     Response, status)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from correspondence import auth, resources
from correspondence.db.deps import get_db_asession
from correspondence.deps import get_organization_by_slug
from correspondence.models import Organization, User

router = APIRouter()


@router.get("/")
async def root(
    request: Request,
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

        return RedirectResponse(
            url=request.url_for(
                "organization_detail", organization_slug=organization.slug
            )
        )

    return RedirectResponse(url=request.url_for("signin"))


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
    user = await auth.login(asession, form.email, form.password)
    token = auth.authenticate(user, response)

    return {"token": token}


@router.get("/signin")
async def signin(
    request: Request,
    asession: AsyncSession = Depends(get_db_asession),
):
    return request.app.templates.TemplateResponse(
        request=request,
        name="signin.html",
        context={"form": {}},
    )


@router.post("/signin")
async def signin_complete(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    asession: AsyncSession = Depends(get_db_asession),
) -> RedirectResponse:
    try:
        user = await auth.login(asession, email, password)
    except RequestValidationError as e:
        return request.app.templates.TemplateResponse(
            request=request,
            name="signin.html",
            context={
                "errors": e.errors(),
                "form": {"email": email, "password": password},
            },
        )
    else:
        response = RedirectResponse(
            url=request.url_for("root"), status_code=status.HTTP_303_SEE_OTHER
        )
        auth.authenticate(user, response)
        return response


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
    division_by_zero = 1 / 0  # noqa
