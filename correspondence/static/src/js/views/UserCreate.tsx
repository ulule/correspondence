import * as React from "react";

import Navbar from "./Navbar";
import Modal from "../components/Modal";
import UserForm from "./UserForm";
import { AppContext } from "../contexts";
import { User } from "../types";

export default function UserCreate({}) {
  const [modalVisible, setModalVisible] = React.useState(false);

  const [submit, setSubmit] = React.useState(false);

  const { organization } = React.useContext(AppContext);

  return (
    <>
      <Navbar
        onUserCreateBtnClick={() => {
          setModalVisible(true);
        }}
      />
      <Modal
        onCloseClick={() => {
          setModalVisible(false);
        }}
        visible={modalVisible}
        title="Create a new contact"
        onSaveClick={() => {
          setSubmit(true);
        }}
      >
        <UserForm
          submit={submit}
          onSubmit={() => setSubmit(false)}
          onUserCreate={(user: User) => {
            setModalVisible(false);
            history.pushState(
              {},
              "",
              `/organizations/${organization.slug}/conversations/${user.id}/`
            );
          }}
        />
      </Modal>
    </>
  );
}
