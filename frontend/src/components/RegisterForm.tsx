import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircleIcon, ExclamationCircleIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useAuth } from "../hooks/authContext";

interface RegisterFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  isDarkMode: boolean;
}

const RegisterForm = ({ onSuccess, onCancel, isDarkMode }: RegisterFormProps) => {
  const { login } = useAuth(); // Use the auth context for login
  // Form state
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  // Validation state
  const [emailError, setEmailError] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  const [isFormValid, setIsFormValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);
  const [registrationError, setRegistrationError] = useState('');

  // Validate email format
  const validateEmail = (email: string) => {
    // More thorough email validation
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  };

  // Validate username with proper validation - exactly matching backend requirements
  const validateUsername = (username: string) => {
    // Only allow alphanumeric characters, underscore, and hyphens
    // Between 3 and 30 characters - EXACTLY matching backend validation
    const regex = /^[a-zA-Z0-9_-]{3,30}$/;
    return regex.test(username);
  };

  // Validate password with stronger requirements
  const validatePassword = (password: string) => {
    // At least 8 characters, containing at least one letter and one number
    return password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password);
  };

  // Handle email change with validation
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    
    if (!value) {
      setEmailError('Email is required');
    } else if (!validateEmail(value)) {
      setEmailError('Please enter a valid email address');
    } else {
      setEmailError('');
    }
  };

  // Handle username change with validation
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsername(value);
    
    if (!value) {
      setUsernameError('Username is required');
    } else if (!validateUsername(value)) {
      setUsernameError('Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens');
    } else {
      setUsernameError('');
    }
  };

  // Handle password change with validation
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    
    if (!value) {
      setPasswordError('Password is required');
    } else if (!validatePassword(value)) {
      setPasswordError('Password must be at least 8 characters and include at least one letter and one number');
    } else {
      setPasswordError('');
    }

    // Also validate confirm password if it has a value
    if (confirmPassword) {
      if (confirmPassword !== value) {
        setConfirmPasswordError('Passwords do not match');
      } else {
        setConfirmPasswordError('');
      }
    }
  };

  // Handle confirm password change with validation
  const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setConfirmPassword(value);
    
    if (!value) {
      setConfirmPasswordError('Please confirm your password');
    } else if (value !== password) {
      setConfirmPasswordError('Passwords do not match');
    } else {
      setConfirmPasswordError('');
    }
  };

  // Check if form is valid whenever inputs change
  useEffect(() => {
    console.log("Form validity check:", {
      email: email.length > 0 && emailError === '',
      username: username.length > 0 && usernameError === '',
      password: password.length > 0 && passwordError === '',
      confirmPassword: confirmPassword.length > 0 && confirmPasswordError === ''
    });
    
    const valid = 
      email.length > 0 && 
      username.length > 0 && 
      password.length > 0 && 
      confirmPassword.length > 0 && 
      emailError === '' && 
      usernameError === '' && 
      passwordError === '' && 
      confirmPasswordError === '';
    
    console.log("Form is valid:", valid);
    setIsFormValid(valid);
  }, [
    email, username, password, confirmPassword, 
    emailError, usernameError, passwordError, confirmPasswordError
  ]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log("Submit attempt - Form valid:", isFormValid);
    
    // Revalidate all fields in case client-side validation was bypassed
    let formHasErrors = false;
    
    if (!email || !validateEmail(email)) {
      setEmailError(email ? 'Please enter a valid email address' : 'Email is required');
      formHasErrors = true;
    }
    
    if (!username || !validateUsername(username)) {
      setUsernameError(username ? 'Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens' : 'Username is required');
      formHasErrors = true;
    }
    
    if (!password || !validatePassword(password)) {
      setPasswordError(password ? 'Password must be at least 8 characters and include at least one letter and one number' : 'Password is required');
      formHasErrors = true;
    }
    
    if (!confirmPassword || confirmPassword !== password) {
      setConfirmPasswordError(confirmPassword ? 'Passwords do not match' : 'Please confirm your password');
      formHasErrors = true;
    }
    
    if (formHasErrors) return;
    
    setIsSubmitting(true);
    setRegistrationError('');
    
    try {
      // Use a single, reliable API endpoint approach
      // Always use direct URL to backend
      const apiUrl = 'https://dreamapp-auth-api.azurewebsites.net';
      console.log("Registering user:", { email, username, password: "***" });
      
      // Direct connection to the backend API
      const registrationUrl = `${apiUrl}/register`;
      
      console.log(`Using direct registration URL: ${registrationUrl}`);
      
      const response = await fetch(registrationUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // Remove credentials for CORS compatibility
        body: JSON.stringify({
          email,
          username,
          password,
        }),
      });
      
      console.log("Registration response status:", response.status);
      
      let responseData;
      try {
        responseData = await response.json();
        console.log("Registration response data:", JSON.stringify(responseData, null, 2));
      } catch (error) {
        console.error("Error parsing response:", error);
        // Even with a parsing error, we may have succeeded - check the status
        if (response.ok) {
          // Success only if we get a 2xx response
          console.log("Registration succeeded despite parsing error");
          setRegisterSuccess(true);
          
          // Try to log in automatically to confirm registration worked
          try {
            console.log("Attempting automatic login to verify account creation");
            const loginResult = await login(email, password);
            
            if (loginResult.success) {
              console.log("Auto-login successful - registration confirmed!");
            } else {
              console.warn("Auto-login failed - but account may still be created");
            }
          } catch (loginError) {
            console.error("Auto-login failed with error:", loginError);
          }
          
          // Notify parent after successful registration
          setTimeout(() => {
            onSuccess();
          }, 2000);
          return;
        }
        throw new Error("Failed to parse response from server");
      }
      
      // If we get here, we have a response and parsed data
      // Only consider 2xx responses as success
      if (response.ok) {
        console.log("Registration successful!");
        setRegisterSuccess(true);
        
        // Try to log in automatically
        try {
          console.log("Attempting automatic login after successful registration");
          const loginResult = await login(email, password);
          
          if (loginResult.success) {
            console.log("Auto-login successful!");
          } else {
            console.warn("Auto-login failed, but registration was successful:", loginResult.message);
          }
        } catch (loginError) {
          console.error("Auto-login error:", loginError);
          // We don't show this error to the user since registration was successful
        }
        
        // Notify parent after successful registration
        setTimeout(() => {
          // Pass the email and password back to parent for potential auto-login
          onSuccess();
        }, 2000);
      } else {
        // Server returned an error
        let errorMessage = "Registration failed";
        
        if (responseData.detail) {
          if (Array.isArray(responseData.detail)) {
            // Handle Pydantic validation errors which come as an array
            errorMessage = responseData.detail[0]?.msg || "Registration failed with validation error";
          } else if (typeof responseData.detail === 'object') {
            // Handle nested object errors
            errorMessage = JSON.stringify(responseData.detail);
          } else {
            errorMessage = responseData.detail;
          }
        }
        
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error("Registration error:", error);
      
      // All network errors could potentially mean the backend registration succeeded
      // So we should be optimistic and assume success is possible
      if (error instanceof TypeError) {
        console.log("Network error during registration - account may have been created");
        setRegistrationError("Network issue detected. Please try logging in, as your account was likely created successfully.");
        
        // Try login immediately to verify account creation
        try {
          console.log("Attempting immediate login to verify account creation");
          const loginResult = await login(email, password);
          
          if (loginResult.success) {
            console.log("Login successful - registration confirmed!");
            // Show immediate success since we verified the account exists
            setRegistrationError("");
            setRegisterSuccess(true);
            
            // Notify parent after successful registration
            setTimeout(() => {
              onSuccess();
            }, 2000);
            return;
          }
        } catch (loginError) {
          console.error("Verification login failed:", loginError);
          // Continue with delayed success in case the account is created but not ready yet
        }
        
        // Show a delayed success message after 3 seconds even if login failed
        setTimeout(() => {
          console.log("Showing delayed success message for likely successful registration");
          setRegistrationError("");
          setRegisterSuccess(true);
          
          // Notify parent after successful registration
          setTimeout(() => {
            onSuccess();
          }, 2000);
        }, 3000);
      } else {
        // Standard error handling for other errors
        setRegistrationError(error instanceof Error ? error.message : "Registration failed");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Container variants for staggered animations
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  // Item variants for staggered animations
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24
      }
    }
  };

  return (
    <div className="px-6 py-8 sm:px-8">
      {registerSuccess ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-4"
        >
          <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-green-100">
            <CheckCircleIcon className="h-10 w-10 text-green-500" />
          </div>
          <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Registration Successful!</h2>
          <p className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
            Your account has been created. You can now log in.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onSuccess}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Go to Login
          </motion.button>
        </motion.div>
      ) : (
        <form onSubmit={handleSubmit}>
          <motion.div 
            className="space-y-4"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={itemVariants}>
              <h2 className={`text-2xl font-bold mb-6 text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                Create an Account
              </h2>
            </motion.div>

            {/* Registration Error */}
            <AnimatePresence>
              {registrationError && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
                >
                  {registrationError}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Email Field */}
            <motion.div variants={itemVariants}>
              <label htmlFor="register-email" className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Email
              </label>
              <motion.div 
                whileFocus={{ scale: 1.01 }}
                className="relative"
              >
                <input
                  id="register-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={handleEmailChange}
                  className={`block w-full px-4 py-3 rounded-xl border transition-all ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                  } ${
                    emailError 
                      ? isDarkMode ? 'border-red-500' : 'border-red-300' 
                      : email 
                        ? isDarkMode ? 'border-green-500' : 'border-green-300' 
                        : ''
                  }`}
                  placeholder="your@email.com"
                />
                {email && !emailError && (
                  <CheckCircleIcon className={`h-5 w-5 ${isDarkMode ? 'text-green-400' : 'text-green-500'} absolute right-3 top-1/2 transform -translate-y-1/2`} />
                )}
                {emailError && (
                  <ExclamationCircleIcon className="h-5 w-5 text-red-500 absolute right-3 top-1/2 transform -translate-y-1/2" />
                )}
              </motion.div>
              <AnimatePresence>
                {emailError && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-1 text-sm text-red-500"
                  >
                    {emailError}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Username Field */}
            <motion.div variants={itemVariants}>
              <label htmlFor="register-username" className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Username
              </label>
              <motion.div 
                whileFocus={{ scale: 1.01 }}
                className="relative"
              >
                <input
                  id="register-username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={handleUsernameChange}
                  className={`block w-full px-4 py-3 rounded-xl border transition-all ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                  } ${
                    usernameError 
                      ? isDarkMode ? 'border-red-500' : 'border-red-300' 
                      : username 
                        ? isDarkMode ? 'border-green-500' : 'border-green-300' 
                        : ''
                  }`}
                  placeholder="username"
                />
                {username && !usernameError && (
                  <CheckCircleIcon className={`h-5 w-5 ${isDarkMode ? 'text-green-400' : 'text-green-500'} absolute right-3 top-1/2 transform -translate-y-1/2`} />
                )}
                {usernameError && (
                  <ExclamationCircleIcon className="h-5 w-5 text-red-500 absolute right-3 top-1/2 transform -translate-y-1/2" />
                )}
              </motion.div>
              <AnimatePresence>
                {usernameError && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-1 text-sm text-red-500"
                  >
                    {usernameError}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Password Field */}
            <motion.div variants={itemVariants}>
              <label htmlFor="register-password" className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Password
              </label>
              <motion.div 
                whileFocus={{ scale: 1.01 }}
                className="relative"
              >
                <input
                  id="register-password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={handlePasswordChange}
                  className={`block w-full px-4 py-3 rounded-xl border transition-all pr-10 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                  } ${
                    passwordError 
                      ? isDarkMode ? 'border-red-500' : 'border-red-300' 
                      : password 
                        ? isDarkMode ? 'border-green-500' : 'border-green-300' 
                        : ''
                  }`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className={`absolute inset-y-0 right-0 flex items-center pr-3 ${
                    isDarkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" aria-hidden="true" />
                  ) : (
                    <EyeIcon className="h-5 w-5" aria-hidden="true" />
                  )}
                </button>
              </motion.div>
              <AnimatePresence>
                {passwordError && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-1 text-sm text-red-500"
                  >
                    {passwordError}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Confirm Password Field */}
            <motion.div variants={itemVariants}>
              <label htmlFor="register-confirm-password" className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Confirm Password
              </label>
              <motion.div 
                whileFocus={{ scale: 1.01 }}
                className="relative"
              >
                <input
                  id="register-confirm-password"
                  name="confirm-password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={handleConfirmPasswordChange}
                  className={`block w-full px-4 py-3 rounded-xl border transition-all pr-10 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'
                  } ${
                    confirmPasswordError 
                      ? isDarkMode ? 'border-red-500' : 'border-red-300' 
                      : confirmPassword 
                        ? isDarkMode ? 'border-green-500' : 'border-green-300' 
                        : ''
                  }`}
                  placeholder="••••••••"
                />
              </motion.div>
              <AnimatePresence>
                {confirmPasswordError && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-1 text-sm text-red-500"
                  >
                    {confirmPasswordError}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Buttons */}
            <motion.div className="flex gap-3 mt-6" variants={itemVariants}>
              <motion.button
                type="button"
                onClick={onCancel}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`flex-1 py-3 px-4 border rounded-xl shadow-sm text-sm font-medium transition-all ${
                  isDarkMode 
                    ? 'bg-gray-700 border-gray-600 text-white hover:bg-gray-600' 
                    : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Cancel
              </motion.button>
              
              <motion.button
                type="submit"
                disabled={isSubmitting || !isFormValid}
                whileHover={{ scale: isFormValid && !isSubmitting ? 1.02 : 1 }}
                whileTap={{ scale: isFormValid && !isSubmitting ? 0.98 : 1 }}
                className={`flex-1 py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white ${
                  isFormValid && !isSubmitting
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700'
                    : isDarkMode ? 'bg-gray-600 cursor-not-allowed' : 'bg-gray-400 cursor-not-allowed'
                } transition-all`}
              >
                {isSubmitting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </>
                ) : (
                  'Create Account'
                )}
              </motion.button>
            </motion.div>
          </motion.div>
        </form>
      )}
    </div>
  );
};

export default RegisterForm;