import "@fortawesome/fontawesome-free/js/all";
import ReactDOM from "react-dom/client";

import PropTypes from "prop-types";
import React, { useState } from "react";
import api from "./api";
import Navbar from "./views/Navbar";
import Modal from "./components/Modal";
import UserForm from "./views/UserForm";
import ConversationWrapper from "./views/ConversationWrapper";
import sanitize from "./utils/sanitize";
import { BrowserRouter, Route, Routes } from "react-router-dom";

const Conversations = ({
  authenticatedUser,
  managers,
  organization,
  countries
} = props) => {
  const initialState = {
    conversation: null,
    isNewConversation: false,
    isNewUser: false,
    userCreateErrors: []
  };

  let history;

  const [state, setState] = useState(initialState);

  const { isNewUser, userCreateErrors } = state;

  const onUserCreate = async props => {
    try {
      const values = sanitize(props.values);
      const res = await api.post(
        `/organizations/${organization.slug}/users/`,
        sanitize(values)
      );

      setState({
        ...state,
        ...{ isNewUser: false }
      });

      history.push(`/conversations/${res.data.id}`);

      if (props.onSuccess && typeof props.onSuccess === "function") {
        props.onSuccess();
      }
    } catch (e) {
      setState({
        ...state,
        ...{ userCreateErrors: e.response.data.detail }
      });
    }
  };

  return (
    <div className="conversations">
      <Navbar
        onUserCreateBtnClick={() => {
          setState({
            ...state,
            ...{ isNewUser: true, userCreateErrors: [] }
          });
        }}
      />
      <Modal
        onCloseClick={() => {
          setState({
            ...state,
            ...{ isNewUser: false }
          });
        }}
        visible={isNewUser}
        title="Create a new contact"
        onSave={onUserCreate}
      >
        <UserForm
          errors={userCreateErrors}
          countries={countries}
          visible={isNewUser}
          managers={managers}
          authenticatedUser={authenticatedUser}
        />
      </Modal>

      <BrowserRouter>
        <Routes>
          <Route
            path="/organizations/:slug/conversations?"
            exact
            element={
              <ConversationWrapper
                organization={organization}
                authenticatedUser={authenticatedUser}
                countries={countries}
                managers={managers}
              />
            }
          />
          <Route
            path="/organizations/:slug/conversations/:id"
            exact
            element={
              <ConversationWrapper
                organization={organization}
                authenticatedUser={authenticatedUser}
                countries={countries}
                managers={managers}
              />
            }
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
};

Conversations.propTypes = {
  authenticatedUser: PropTypes.any.isRequired,
  countries: PropTypes.any.isRequired,
  organization: PropTypes.any.isRequired,
  managers: PropTypes.arrayOf(PropTypes.any).isRequired
};

const loadManagers = async () => {
  const res = await api.get(`/users/?is_staff=1`);
  return res.data;
};

window.addEventListener("DOMContentLoaded", () => {
  (async () => {
    const managers = await loadManagers();

    const { organization, countries } = window.CDE;

    const supportedCountries = countries.filter(
      entry => organization.supported_countries.indexOf(entry[0]) !== -1
    );

    const root = ReactDOM.createRoot(
      document.getElementById("conversations-container")
    );

    root.render(
      <Conversations
        authenticatedUser={window.CDE.authenticatedUser}
        organization={organization}
        countries={supportedCountries}
        managers={managers.data}
      />
    );
  })();
});
