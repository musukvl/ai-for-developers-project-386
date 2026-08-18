import { userName } from './useUserName';
import NameEntry from './NameEntry.vue';
import CreateCalendarForm from '../owner/CreateCalendarForm.vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const __VLS_ctx = {
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
if (!__VLS_ctx.userName) {
    const __VLS_0 = NameEntry;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({
        ...{ 'onEntered': {} },
    }));
    const __VLS_2 = __VLS_1({
        ...{ 'onEntered': {} },
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    let __VLS_5;
    const __VLS_6 = {
        /** @type {typeof __VLS_5.entered} */
        onEntered: (() => { }),
    };
    var __VLS_7;
    var __VLS_3;
    var __VLS_4;
}
else {
    const __VLS_8 = CreateCalendarForm;
    // @ts-ignore
    const __VLS_9 = __VLS_asFunctionalComponent1(__VLS_8, new __VLS_8({
        ...{ 'onCreated': {} },
    }));
    const __VLS_10 = __VLS_9({
        ...{ 'onCreated': {} },
    }, ...__VLS_functionalComponentArgsRest(__VLS_9));
    let __VLS_13;
    const __VLS_14 = {
        /** @type {typeof __VLS_13.created} */
        onCreated: (__VLS_ctx.router.push),
    };
    var __VLS_15;
    var __VLS_11;
    var __VLS_12;
}
// @ts-ignore
[userName, router,];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
