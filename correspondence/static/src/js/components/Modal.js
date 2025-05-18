import React, { useState, useEffect } from "react";
import classNames from "classnames";

const Modal = props => {
  const { visible = false, onCloseClick, title, onSave } = props;

  const [submit, setSubmit] = useState(false);

  const onSubmit = props => {
    onSave({
      ...props,
      onSuccess: () => {
        setSubmit(false);

        if (props.onSuccess && typeof props.onSuccess === "function") {
          props.onSuccess();
        }
      }
    });
  };

  useEffect(() => {
    const handleKeydown = evt => {
      // handle ESC key
      if (evt.keyCode === 27) {
        onCloseClick();
      }
    };

    document.addEventListener("keydown", handleKeydown, false);

    return () => {
      document.removeEventListener("keydown", handleKeydown, false);
    };
  });

  const onErrors = values => {
    setSubmit(false);
  };

  return (
    <div
      className={classNames({
        modal: true,
        "is-active": visible
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
          {React.cloneElement(props.children, { onSubmit, submit, onErrors })}
        </section>
        <footer className="modal-card-foot">
          <button
            className={classNames({
              button: true,
              "is-success": true,
              "is-loading": submit
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
};

export default Modal;
