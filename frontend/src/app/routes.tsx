import { Route, Routes } from 'react-router-dom';

import AdminPage from '@/pages/admin/AdminPage';
import ConversationDetailPage from '@/pages/conversations/ConversationDetailPage';
import ConversationsPage from '@/pages/conversations/ConversationsPage';
import NotFoundPage from '@/pages/not-found/NotFoundPage';
import SellerDetailPage from '@/pages/sellers/SellerDetailPage';
import { ROUTES } from '@/shared/config/routes';

import DefaultLayout from './layouts/DefaultLayout';

const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<DefaultLayout />}>
        <Route path={ROUTES.HOME} element={<AdminPage />} />
        <Route path={ROUTES.CONVERSATIONS} element={<ConversationsPage />} />
        <Route path={`${ROUTES.CONVERSATIONS}/:id`} element={<ConversationDetailPage />} />
        <Route path={`${ROUTES.SELLERS}/:id`} element={<SellerDetailPage />} />
        <Route path='*' element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
