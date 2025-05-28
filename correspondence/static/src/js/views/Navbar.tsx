import * as React from "react";

type NavbarProps = {
  onUserCreateBtnClick: () => void;
};

export default function Navbar({
  onUserCreateBtnClick,
}: NavbarProps): React.ReactElement {
  return (
    <nav
      className="navbar conversations__header"
      role="navigation"
      aria-label="main navigation"
    >
      <div className="navbar-menu">
        <div className="navbar-start">
          <a className="navbar-item" href="/">
            <i className="fas fa-home"></i>
          </a>
        </div>
        <div className="navbar-end">
          <div className="navbar-item">
            <div className="buttons">
              <a className="button is-info" onClick={onUserCreateBtnClick}>
                <strong>Create a contact</strong>
                <span className="icon is-small">
                  <i className="fas fa-plus"></i>
                </span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
