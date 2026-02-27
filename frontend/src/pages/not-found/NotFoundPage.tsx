import { useNavigate } from 'react-router-dom';

import { ROUTES } from '@/shared/config/routes';
import { Button } from '@/shared/ui/Button';

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className='flex flex-1 flex-col items-center justify-center gap-4'>
      <h1 className='text-4xl font-bold'>404</h1>
      <p className='text-muted-foreground'>페이지를 찾을 수 없습니다.</p>
      <Button variant='outline' onClick={() => navigate(ROUTES.HOME)}>
        홈으로 돌아가기
      </Button>
    </div>
  );
};

export default NotFoundPage;
