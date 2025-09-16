import React from 'react';
import { Card, CardProps, CardContent, Typography, Box } from '@mui/material';
import { colors } from '../theme';

interface ReckonCardProps extends Omit<CardProps, 'children'> {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  hover?: boolean;
}

export const ReckonCard: React.FC<ReckonCardProps> = ({
  title,
  subtitle,
  icon,
  children,
  hover = true,
  ...cardProps
}) => {
  return (
    <Card
      {...cardProps}
      sx={{
        p: 3,
        borderRadius: 3,
        border: `1px solid ${colors.divider}`,
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        transition: 'all 0.2s ease-in-out',
        ...(hover && {
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            transform: 'translateY(-1px)',
            borderColor: colors.primary.light,
          },
        }),
        ...cardProps.sx,
      }}
    >
      {(title || subtitle || icon) && (
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          {icon && (
            <Box sx={{ color: colors.primary.main, display: 'flex' }}>
              {icon}
            </Box>
          )}
          <Box sx={{ flex: 1 }}>
            {title && (
              <Typography variant="h6" component="h3" sx={{ mb: 0.5 }}>
                {title}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      )}
      {children && <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>{children}</CardContent>}
    </Card>
  );
};