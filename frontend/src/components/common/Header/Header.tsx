import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Avatar, Menu, MenuItem, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircle from '@mui/icons-material/AccountCircle';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsIcon from '@mui/icons-material/Settings';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import { Link as RouterLink, useNavigate } from 'react-router-dom'; // Assuming use of React Router

interface HeaderProps {
  onDrawerToggle?: () => void; // For mobile sidebar toggle
  isSidebarOpen?: boolean;
}

const Header: React.FC<HeaderProps> = ({ onDrawerToggle, isSidebarOpen }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    // Add logout logic here (e.g., clear token, redirect)
    console.log('User logged out');
    handleClose();
    navigate('/login'); // Redirect to login page
  };
  
  const handleProfile = () => {
    navigate('/profile');
    handleClose();
  }

  const handleSettings = () => {
    navigate('/settings');
    handleClose();
  }

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        // width: { sm: `calc(100% - ${isSidebarOpen ? 240 : 0}px)` }, // Adjust width if sidebar is persistent
        // ml: { sm: `${isSidebarOpen ? 240 : 0}px` }, // Adjust margin if sidebar is persistent
      }}
      elevation={1}
    >
      <Toolbar>
        {onDrawerToggle && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }} // Show only on small screens if sidebar is present
          >
            <MenuIcon />
          </IconButton>
        )}
        <Typography variant="h6" noWrap component={RouterLink} to="/dashboard" sx={{ flexGrow: 1, color: 'inherit', textDecoration: 'none' }}>
          Legal Application System
        </Typography>
        <Box>
          <IconButton color="inherit">
            <NotificationsIcon />
          </IconButton>
          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={open}
            onClose={handleClose}
            sx={{mt: '45px'}}
          >
            <MenuItem onClick={handleProfile}>
              <Avatar sx={{ width: 24, height: 24, mr: 1, bgcolor: 'secondary.main' }} /> Profile
            </MenuItem>
            <MenuItem onClick={handleSettings}>
              <SettingsIcon sx={{ mr: 1 }} /> Settings
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ExitToAppIcon sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
