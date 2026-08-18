import { ref } from 'vue';
import { setApiUserName } from '../shared/apiClient';
const storedName = sessionStorage.getItem('calls-calendar-user') ?? '';
export const userName = ref(storedName);
setApiUserName(storedName);
export function rememberUserName(name) {
    userName.value = name;
    sessionStorage.setItem('calls-calendar-user', name);
    setApiUserName(name);
}
