import { useEffect, useState } from "react";
import { useAuth } from "../hooks/authContext"; 

export const Profile = () => {
  const { fetchWithAuth, logout } = useAuth(); // Get helper from context
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await fetchWithAuth(`${import.meta.env.VITE_API_URL}/api/profile`);
        if (!res.ok) throw new Error("Failed to fetch profile");
        const data = await res.json();
        setProfile(data);
      } catch (err) {
        console.error(err);
      }
    };

    loadProfile();
  }, [fetchWithAuth]);

  return (
    <div>
      <h2>Profile</h2>
      {profile ? (
        <pre>{JSON.stringify(profile, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
      <button onClick={logout}>Logout</button>
    </div>
  );
};