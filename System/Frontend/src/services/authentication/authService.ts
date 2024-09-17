// Safe AuthData to the local Browser stroage
export const saveAuthData = (token: string, role: string, userID: string ) => {
    localStorage.setItem('jwt', token);
    localStorage.setItem('userRole', role);
    localStorage.setItem('userID', userID);
  };
  
  // Load AuthData from the local Browser stroage
  export const getAuthData = () => {
    return {
      token: localStorage.getItem('jwt') || '',
      role: localStorage.getItem('userRole') || '',
      userID: localStorage.getItem('userID') || '',
    };
  };
  
  // Delete AuthData from the local Browser stroage
  export const clearAuthData = () => {
    localStorage.removeItem('jwt');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userID');
  };