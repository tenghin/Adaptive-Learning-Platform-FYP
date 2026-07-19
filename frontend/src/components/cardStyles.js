export const lineClampSx = (lines) => ({
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  display: '-webkit-box',
  WebkitBoxOrient: 'vertical',
  WebkitLineClamp: lines,
});

export const interactiveCardSx = {
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 2,
  transition: 'transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 20px 44px rgba(18, 50, 79, 0.12)',
    borderColor: 'rgba(18, 50, 79, 0.14)',
  },
};

export const cardContentSx = {
  flexGrow: 1,
  display: 'flex',
  flexDirection: 'column',
  gap: 1.5,
  p: 3,
};

export const cardActionsSx = {
  px: 3,
  pb: 3,
  pt: 0,
  mt: 'auto',
};
