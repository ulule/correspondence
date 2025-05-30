import * as React from "react";
import classNames from "classnames";
import { OnUserCreateEvent } from "../types";

type ModalChildProps = {};

type ModalProps = {
  visible: boolean;
  onCloseClick: () => void;
  title: string;
  loading?: boolean;
  onSaveClick: () => void;
  children: React.ReactElement<ModalChildProps>;
};

export default function Modal({
  visible,
  onCloseClick,
  loading,
  title,
  onSaveClick,
  children,
}: ModalProps): React.ReactElement {
  React.useEffect(() => {
    const handleKeydown = (evt: KeyboardEvent) => {
      // handle ESC key
      if (evt.key === "Escape") {
        onCloseClick();
      }
    };

    document.addEventListener("keydown", handleKeydown, false);

    return () => {
      document.removeEventListener("keydown", handleKeydown, false);
    };
  });

  return (
    <div
      className={classNames({
        modal: true,
        "is-active": visible,
      })}
    >
      <div className="modal-background"></div>
      <div className="modal-card">
        <header className="modal-card-head">
          <p className="modal-card-title">{title}</p>
          <button
            className="delete"
            aria-label="close"
            onClick={onCloseClick}
          ></button>
        </header>
        <section className="modal-card-body">
          {React.cloneElement(
            children as React.ReactElement<ModalChildProps>,
            {}
          )}
        </section>
        <footer className="modal-card-foot">
          <button
            className={classNames({
              button: true,
              "is-success": true,
              "is-loading": !!loading,
            })}
            onClick={onSaveClick}
          >
            Save changes
          </button>
          <button className="button" onClick={onCloseClick}>
            Cancel
          </button>
        </footer>
      </div>
    </div>
  );
}
