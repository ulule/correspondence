import { atom } from "jotai";

import { Conversation, User, Message } from "./types";

export const conversationAtom = atom<Conversation | null>();

export const selectedUsersAtom = atom<User[] | null>();

export const userAtom = atom<User | null>();

export const messagesAtom = atom<Message[] | null>();
