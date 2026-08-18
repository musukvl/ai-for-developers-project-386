import { ref } from 'vue';
import { api } from '../shared/apiClient';
import { userName } from '../shell/useUserName';
const emit = defineEmits();
const error = ref('');
async function create() {
    try {
        const result = await api('/calendars', { method: 'POST', body: JSON.stringify({ ownerId: userName.value }) });
        emit('created', result.calendarUrl);
    }
    catch (reason) {
        error.value = reason instanceof Error ? reason.message : 'Calendar creation failed.';
    }
}
const __VLS_ctx = {
    ...{},
    ...{},
    ...{},
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
__VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
    ...{ class: "space-y-4" },
});
/** @type {__VLS_StyleScopedClasses['space-y-4']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({
    ...{ class: "text-2xl font-bold" },
});
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "text-red-700" },
    });
    /** @type {__VLS_StyleScopedClasses['text-red-700']} */ ;
    (__VLS_ctx.error);
}
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
    ...{ onClick: (__VLS_ctx.create) },
    'data-testid': "create-calendar",
});
// @ts-ignore
[error, error, create,];
const __VLS_export = (await import('vue')).defineComponent({
    __typeEmits: {},
});
export default {};
