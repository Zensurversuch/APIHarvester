export const saveAuthData = (token: string, role: string, userID: string ) => {
    localStorage.setItem('jwt', token);
    localStorage.setItem('userRole', role);
    localStorage.setItem('userID', userID);
  };
  
  export const getAuthData = () => {
    return {
      token: localStorage.getItem('jwt') || '',
      role: localStorage.getItem('userRole') || '',
      userID: localStorage.getItem('userID') || '',
    };
  };
  
  export const clearAuthData = () => {
    localStorage.removeItem('jwt');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userID');
  };