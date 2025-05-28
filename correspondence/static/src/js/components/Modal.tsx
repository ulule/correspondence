import * as React from "react";
import classNames from "classnames";
import { OnUserCreateEvent } from "../types";

type ModalChildProps = {
  onSubmit: (props: OnUserCreateEvent) => void
  submit: boolean
  onErrors: () => void
}

type ModalProps = {
  visible: boolean;
  onCloseClick: () => void;
  title: string;
  onSave: (props: OnUserCreateEvent) => void | Promise<void>;
  children: React.ReactElement<ModalChildProps>;
};

export default function Modal({
  visible,
  onCloseClick,
  title,
  onSave,
  children,
}: ModalProps): React.ReactElement {
  const [submit, setSubmit] = React.useState(false);

  const onSubmit = ({ onSuccess, ...props }: OnUserCreateEvent) => {
    onSave({
      ...props,
      onSuccess: () => {
        setSubmit(false);

        if (onSuccess) {
          onSuccess();
        }
      },
    });
  };

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

  const onErrors = () => {
    setSubmit(false);
  };

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
          {React.cloneElement(children as React.ReactElement<ModalChildProps>, { onSubmit, submit, onErrors })}
        </section>
        <footer className="modal-card-foot">
          <button
            className={classNames({
              button: true,
              "is-success": true,
              "is-loading": submit,
            })}
            onClick={() => {
              setSubmit(true);
            }}
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