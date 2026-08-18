import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { userName } from './useUserName';
import NameEntry from './NameEntry.vue';
import OwnerView from '../owner/OwnerView.vue';
import VisitorView from '../visitor/VisitorView.vue';
const route = useRoute();
const ownerId = computed(() => String(route.params.ownerId).toLowerCase());
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
else if (__VLS_ctx.userName === __VLS_ctx.ownerId) {
    const __VLS_8 = OwnerView;
    // @ts-ignore
    const __VLS_9 = __VLS_asFunctionalComponent1(__VLS_8, new __VLS_8({
        ownerId: (__VLS_ctx.ownerId),
    }));
    const __VLS_10 = __VLS_9({
        ownerId: (__VLS_ctx.ownerId),
    }, ...__VLS_functionalComponentArgsRest(__VLS_9));
    var __VLS_13;
    var __VLS_11;
}
else {
    const __VLS_14 = VisitorView;
    // @ts-ignore
    const __VLS_15 = __VLS_asFunctionalComponent1(__VLS_14, new __VLS_14({
        ownerId: (__VLS_ctx.ownerId),
    }));
    const __VLS_16 = __VLS_15({
        ownerId: (__VLS_ctx.ownerId),
    }, ...__VLS_functionalComponentArgsRest(__VLS_15));
    var __VLS_19;
    var __VLS_17;
}
// @ts-ignore
[userName, userName, ownerId, ownerId, ownerId,];
const __VLS_export = (await import('vue')).defineComponent({});
export default {};
