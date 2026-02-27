import { useCallback, useEffect } from 'react';

import { Plus } from 'lucide-react';

import type { Message } from '@/entities/message';
import MessageList from '@/entities/message/ui/MessageList';
import { ChatHistoryPopover } from '@/features/chat-history';
import { useOnboardingStore } from '@/features/onboarding';
import { useChat } from '@/features/send-message';
import MessageInput from '@/features/send-message/ui/MessageInput';
import { SuggestedPrompts } from '@/features/suggested-prompts';
import { Button } from '@/shared/ui/Button';

interface ChatPanelProps {
  onToolResult?: (toolName: string) => void;
  inputValue: string;
  onInputChange: (value: string) => void;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
  onSelectPrompt: (prompt: string) => void;
}

const ChatPanel = ({
  onToolResult,
  inputValue,
  onInputChange,
  inputRef,
  onSelectPrompt,
}: ChatPanelProps) => {
  const isGuideCompleted = useOnboardingStore((s) =>
    s.completedMilestones.includes('guide_searched'),
  );

  const {
    messages,
    isStreaming,
    statusMessage,
    error,
    conversationId,
    sendMessage,
    stopStreaming,
    loadConversation,
    resetChat,
  } = useChat({
    onToolResult,
    onAbort: onInputChange,
  });

  useEffect(() => {
    if (isStreaming) {
      useOnboardingStore.getState().lock();
    } else {
      useOnboardingStore.getState().unlock();
    }
  }, [isStreaming]);

  const handleSend = (message: string) => {
    sendMessage(message);
    onInputChange('');

    if (!isGuideCompleted) {
      useOnboardingStore.getState().completeMilestone('guide_searched');
    }
  };

  const handleSelectConversation = useCallback(
    (selectedConversationId: string, selectedMessages: Message[]) => {
      loadConversation(selectedConversationId, selectedMessages);
      onInputChange('');
      inputRef.current?.focus();
    },
    [loadConversation, onInputChange, inputRef],
  );

  const handleNewChat = useCallback(() => {
    resetChat();
    onInputChange('');
    inputRef.current?.focus();
  }, [resetChat, onInputChange, inputRef]);

  return (
    <aside className='flex w-80 flex-col overflow-hidden rounded-t-2xl bg-background shadow-sm lg:w-100'>
      <header className='flex items-center gap-2 pl-5 pr-4 pt-4 pb-3'>
        <h2 className='text-xl font-semibold'>AI 채팅</h2>
        <div className='ml-auto flex items-center gap-1'>
          <Button variant='ghost' size='icon' onClick={handleNewChat} aria-label='새 대화 시작'>
            <Plus className='size-4' />
          </Button>
          <ChatHistoryPopover
            currentConversationId={conversationId}
            onSelectConversation={handleSelectConversation}
          />
        </div>
      </header>

      {error && (
        <div className='mx-4 mt-2 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive'>
          {error}
        </div>
      )}

      {messages.length === 0 ? (
        <div className='flex flex-1 items-center justify-center pb-[15%]'>
          <div data-onboarding='chat-empty-state' className='flex flex-col gap-6 px-4'>
            <div className='flex flex-col items-center'>
              <p className='text-sm text-muted-foreground'>판매자님, 안녕하세요.</p>
              <p className='text-lg font-medium text-foreground'>무엇을 도와드릴까요?</p>
            </div>
            <SuggestedPrompts
              variant='centered'
              onSelect={onSelectPrompt}
              isDisabled={isStreaming}
              categoryFilter={isGuideCompleted ? undefined : 'guide'}
            />
          </div>
        </div>
      ) : (
        <>
          <div className='relative flex flex-1 flex-col overflow-hidden'>
            <MessageList messages={messages} statusMessage={statusMessage} />
            <div className='pointer-events-none absolute right-2.5 bottom-0 left-0 h-8 bg-linear-to-t from-background to-transparent' />
          </div>
          <SuggestedPrompts onSelect={onSelectPrompt} isDisabled={isStreaming} />
        </>
      )}
      <MessageInput
        value={inputValue}
        onChange={onInputChange}
        onSend={handleSend}
        onStop={stopStreaming}
        isStreaming={isStreaming}
        inputRef={inputRef}
      />
    </aside>
  );
};

export default ChatPanel;
