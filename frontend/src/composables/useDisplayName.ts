import { useUIStore } from '@/stores/ui.store';

/**
 * Composable to display entity names respecting the current locale.
 * When locale is 'bn' and a Bengali name exists, shows it; otherwise shows English name.
 */
export function useDisplayName() {
  const uiStore = useUIStore();

  const displayName = (name: string, nameBn?: string | null): string => {
    return uiStore.displayName(name, nameBn);
  };

  return { displayName };
}
