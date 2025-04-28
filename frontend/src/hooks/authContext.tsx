import React, { createContext, useContext, useState, useEffect } from "react";

type AuthContextType = {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
  logout: () => void;
  login: (email: string, password: string) => Promise<{ success: boolean; message: string }>;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const refreshToken = async () => {
    try {
      console.log("Attempting to refresh token...");
      
      // Always use direct URL to backend
      const apiUrl = 'https://dreamapp-auth-api.azurewebsites.net';
      
      // Direct connection to the backend API
      const refreshUrl = `${apiUrl}/refresh`;
        
      console.log(`Using refresh URL: ${refreshUrl}`);
      
      const res = await fetch(refreshUrl, {
        method: "POST",
        // Remove credentials for CORS compatibility
      });
      if (!res.ok) {
        console.log("Token refresh failed with status:", res.status);
        throw new Error("Token refresh failed");
      }
      const data = await res.json();
      console.log("Token refresh successful");
      setAccessToken(data.access_token);
      setIsAuthenticated(true);
      return data.access_token;
    } catch (error) {
      console.log("Token refresh error:", error);
      setAccessToken(null);
      setIsAuthenticated(false);
      return null;
    }
  };

  const login = async (email: string, password: string) => {
    try {
      // Create form data for the API
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);
      
      console.log("Attempting login for:", email);
      
      // Always use direct URL to backend
      const apiUrl = 'https://dreamapp-auth-api.azurewebsites.net';
      
      // Direct connection to the backend API
      const loginUrl = `${apiUrl}/token`;
        
      console.log(`Using login URL: ${loginUrl}`);
      
      console.log("Sending login request WITHOUT credentials");
      const res = await fetch(loginUrl, {
        method: "POST",
        // Remove credentials: "include" which is causing CORS issues
        // When credentials are included, the server must specify an exact origin, not "*"
        body: formData,
      });
      
      console.log("Login response status:", res.status);
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Login failed" }));
        console.error("Login failed:", errorData);
        return { 
          success: false, 
          message: errorData.detail || "Invalid credentials. Please try again." 
        };
      }
      
      // Let's handle the JSON parsing more safely
      try {
        // Clone the response if you need to read it multiple times
        const clonedResponse = res.clone();
        
        try {
          const responseText = await clonedResponse.text();
          console.log("Raw response:", responseText);
        } catch (e) {
          console.log("Could not read raw response", e);
        }
        
        // Now parse the actual response
        const data = await res.json();
        console.log("Login successful, received data:", data);
        
        if (!data.access_token) {
          console.error("No access token in response");
          return { 
            success: false, 
            message: "Server did not return a token. Please try again." 
          };
        }
        
        // Store the token and update authentication state
        setAccessToken(data.access_token);
        setIsAuthenticated(true);
        
        // Store auth flag in localStorage to persist across refreshes
        localStorage.setItem('hasAuth', 'true');
        
        // Return success
        return { success: true, message: "Login successful" };
      } catch (parseError) {
        console.error("Error parsing login response:", parseError);
        return { 
          success: false, 
          message: "Could not parse server response" 
        };
      }
    } catch (error) {
      console.error("Login error:", error);
      return { 
        success: false, 
        message: error instanceof Error ? error.message : "Login failed due to a network error" 
      };
    }
  };

  const fetchWithAuth = async (input: RequestInfo, init: RequestInit = {}) => {
    const res = await fetch(input, {
      ...init,
      headers: {
        ...(init.headers || {}),
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (res.status === 401) {
      const newToken = await refreshToken();
      if (!newToken) throw new Error("Unauthorized");
      const retryRes = await fetch(input, {
        ...init,
        headers: {
          ...(init.headers || {}),
          Authorization: `Bearer ${newToken}`,
          "Content-Type": "application/json",
        },
      });
      return retryRes;
    }

    return res;
  };

  const logout = async () => {
    // Always use direct URL to backend
    const apiUrl = 'https://dreamapp-auth-api.azurewebsites.net';
    
    // Direct connection to the backend API
    const logoutUrl = `${apiUrl}/logout`;
      
    console.log(`Using logout URL: ${logoutUrl}`);
    
    await fetch(logoutUrl, {
      method: "POST",
      // Remove credentials for CORS compatibility
    });
    // Remove auth flag from localStorage
    localStorage.removeItem('hasAuth');
    setAccessToken(null);
    setIsAuthenticated(false);
  };

  // Attempt to refresh token on initial load, but only if we have a cookie
  useEffect(() => {
    // We can't directly check for cookies due to browser security,
    // but we can make a conditional fetch which will only try to refresh
    // if there might be existing auth
    const localStorageHasAuth = localStorage.getItem('hasAuth') === 'true';
    
    if (localStorageHasAuth) {
      console.log("Auth history found, attempting refresh");
      refreshToken();
    } else {
      console.log("No auth history found, skipping token refresh");
    }
  }, []);

  return (
    <AuthContext.Provider value={{ 
      accessToken, 
      setAccessToken, 
      fetchWithAuth, 
      logout, 
      login,
      isAuthenticated
    }}>
      {children}
    </AuthContext.Provider>
  );
};