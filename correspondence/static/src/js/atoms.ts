import { atom } from "jotai";

import { Conversation, User, Message } from "./types";

export const conversationAtom = atom<Conversation | null>();

export const selectedUsersAtom = atom<User[] | null>();

export const userAtom = atom<User | null>();

export const userFormSubmmitting = atom<boolean>(false);

export const submitUserForm = atom<boolean>(false);

export const isNewConversation = atom<boolean>(false);