import { createContext, PropsWithChildren, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, AUTH_UNAUTHORIZED_EVENT, TOKEN_KEY } from "../lib/api";
import type { ChangePasswordPayload, DeleteAccountPayload, MessageResponse, User, UserProfilePayload } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (identifier: string, password: string) => Promise<User>;
  logout: () => void;
  updateProfile: (payload: UserProfilePayload) => Promise<User>;
  changePassword: (payload: ChangePasswordPayload) => Promise<MessageResponse>;
  deleteAccount: (payload: DeleteAccountPayload) => Promise<MessageResponse>;
  uploadAvatar: (file: File) => Promise<User>;
  deleteAvatar: () => Promise<User>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return () => controller.abort();
    }

    api.getMe(controller.signal)
      .then(setUser)
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => logout();
    const handleStorage = (event: StorageEvent) => {
      if (event.key === TOKEN_KEY && !event.newValue) logout();
    };
    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
      window.removeEventListener("storage", handleStorage);
    };
  }, [logout]);

  const login = useCallback(async (identifier: string, password: string) => {
    const token = await api.login(identifier, password);
    localStorage.setItem(TOKEN_KEY, token.access_token);
    try {
      const currentUser = await api.getMe();
      setUser(currentUser);
      setLoading(false);
      return currentUser;
    } catch (cause) {
      localStorage.removeItem(TOKEN_KEY);
      setUser(null);
      throw cause;
    }
  }, []);

  const updateProfile = useCallback(async (payload: UserProfilePayload) => {
    const updated = await api.updateProfile(payload);
    setUser(updated);
    return updated;
  }, []);

  const uploadAvatar = useCallback(async (file: File) => {
    const updated = await api.uploadAvatar(file);
    setUser(updated);
    return updated;
  }, []);

  const changePassword = useCallback((payload: ChangePasswordPayload) => api.changePassword(payload), []);

  const deleteAccount = useCallback(async (payload: DeleteAccountPayload) => {
    const result = await api.deleteAccount(payload);
    logout();
    return result;
  }, [logout]);

  const deleteAvatar = useCallback(async () => {
    const updated = await api.deleteAvatar();
    setUser(updated);
    return updated;
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout, updateProfile, changePassword, deleteAccount, uploadAvatar, deleteAvatar }),
    [changePassword, deleteAccount, deleteAvatar, loading, login, logout, updateProfile, uploadAvatar, user],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth phải được sử dụng bên trong AuthProvider.");
  return context;
}
