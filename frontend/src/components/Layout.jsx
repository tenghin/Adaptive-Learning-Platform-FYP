import { AppBar, Box, Button, Container, Stack, Toolbar, Typography } from '@mui/material';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.jsx';

const baseNavItems = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Courses', to: '/courses' },
  { label: 'Profile', to: '/profile' },
];

export function Layout() {
  const { logout, user } = useAuth();
  const navItems = user?.role === 'admin'
    ? [...baseNavItems, { label: 'Admin', to: '/admin' }]
    : baseNavItems;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background:
          'radial-gradient(circle at top left, rgba(19, 50, 79, 0.08), transparent 30%), linear-gradient(180deg, #f7faff 0%, #eef3f9 100%)',
      }}
    >
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          backdropFilter: 'blur(10px)',
          backgroundColor: 'rgba(18, 50, 79, 0.92)',
        }}
      >
        <Toolbar sx={{ gap: 2, flexWrap: 'wrap' }}>
          <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: 0.4 }}>
            Adaptive Learning Platform
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
            {user ? `Welcome, ${user.first_name}` : 'Personalized learning workspace'}
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
            {navItems.map((item) => (
              <Button
                key={item.to}
                component={NavLink}
                to={item.to}
                variant="text"
                sx={{
                  color: 'white',
                  '&.active': {
                    backgroundColor: 'rgba(255,255,255,0.16)',
                  },
                }}
              >
                {item.label}
              </Button>
            ))}
            <Button variant="contained" color="secondary" onClick={logout}>
              Logout
            </Button>
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
