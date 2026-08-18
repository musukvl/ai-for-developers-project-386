import { onMounted, ref } from 'vue';
import { api } from '../shared/apiClient';
import SlotDayList from '../shared/SlotDayList.vue';
const props = defineProps();
const calendar = ref();
const error = ref('');
const start = ref('');
const end = ref('');
async function load() { try {
    calendar.value = await api(`/calendars/${props.ownerId}/owner`);
}
catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Could not load calendar.';
} }
async function add() { try {
    await api(`/calendars/${props.ownerId}/availability`, { method: 'POST', body: JSON.stringify({ start: new Date(start.value).toISOString(), end: new Date(end.value).toISOString() }) });
    start.value = '';
    end.value = '';
    await load();
}
catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Could not add availability.';
} }
async function remove(slot) { await api(`/calendars/${props.ownerId}/availability/${encodeURIComponent(slot.start)}`, { method: 'DELETE' }); await load(); }
async function cancel(id) { await api(`/calendars/${props.ownerId}/owner/bookings/${id}`, { method: 'DELETE' }); await load(); }
onMounted(load);
const __VLS_ctx = {
    ...{},
    ...{},
    ...{},
    ...{},
};
let __VLS_components;
let __VLS_intrinsics;
let __VLS_directives;
__VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
    ...{ class: "space-y-6" },
});
/** @type {__VLS_StyleScopedClasses['space-y-6']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({
    ...{ class: "text-2xl font-bold" },
});
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
(__VLS_ctx.ownerId);
__VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
__VLS_asFunctionalElement1(__VLS_intrinsics.code, __VLS_intrinsics.code)({});
(__VLS_ctx.ownerId);
__VLS_asFunctionalElement1(__VLS_intrinsics.form, __VLS_intrinsics.form)({
    ...{ onSubmit: (__VLS_ctx.add) },
    ...{ class: "flex flex-wrap gap-2" },
});
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.input)({
    type: "datetime-local",
    required: true,
});
(__VLS_ctx.start);
__VLS_asFunctionalElement1(__VLS_intrinsics.input)({
    type: "datetime-local",
    required: true,
});
(__VLS_ctx.end);
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({});
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "text-red-700" },
    });
    /** @type {__VLS_StyleScopedClasses['text-red-700']} */ ;
    (__VLS_ctx.error);
}
__VLS_asFunctionalElement1(__VLS_intrinsics.h2, __VLS_intrinsics.h2)({
    ...{ class: "text-xl font-semibold" },
});
/** @type {__VLS_StyleScopedClasses['text-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
if (__VLS_ctx.calendar) {
    const __VLS_0 = SlotDayList;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({
        ...{ 'onAction': {} },
        slots: (__VLS_ctx.calendar.availableSlots),
        actionLabel: "Remove",
    }));
    const __VLS_2 = __VLS_1({
        ...{ 'onAction': {} },
        slots: (__VLS_ctx.calendar.availableSlots),
        actionLabel: "Remove",
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    let __VLS_5;
    const __VLS_6 = {
        /** @type {typeof __VLS_5.action} */
        onAction: (__VLS_ctx.remove),
    };
    var __VLS_3;
    var __VLS_4;
}
__VLS_asFunctionalElement1(__VLS_intrinsics.h2, __VLS_intrinsics.h2)({
    ...{ class: "text-xl font-semibold" },
});
/** @type {__VLS_StyleScopedClasses['text-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
if (__VLS_ctx.calendar?.bookings.length) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "space-y-2" },
    });
    /** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
    for (const [booking] of __VLS_vFor((__VLS_ctx.calendar.bookings))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            key: (booking.id),
            ...{ class: "flex justify-between rounded bg-white p-3" },
        });
        /** @type {__VLS_StyleScopedClasses['flex']} */ ;
        /** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
        /** @type {__VLS_StyleScopedClasses['rounded']} */ ;
        /** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
        /** @type {__VLS_StyleScopedClasses['p-3']} */ ;
        (booking.start);
        (booking.visitorName);
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.calendar?.bookings.length))
                        throw 0;
                    return (__VLS_ctx.cancel(booking.id));
                    // @ts-ignore
                    [ownerId, ownerId, add, start, end, error, error, calendar, calendar, calendar, calendar, remove, cancel,];
                } },
        });
        // @ts-ignore
        [];
    }
}
else {
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
}
// @ts-ignore
[];
const __VLS_export = (await import('vue')).defineComponent({
    __typeProps: {},
});
export default {};
