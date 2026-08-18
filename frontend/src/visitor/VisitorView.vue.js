import { onMounted, ref } from 'vue';
import { api, ApiError } from '../shared/apiClient';
import SlotDayList from '../shared/SlotDayList.vue';
import CalendarNotFound from './CalendarNotFound.vue';
const props = defineProps();
const calendar = ref();
const error = ref('');
const notFound = ref(false);
async function load() { try {
    calendar.value = await api(`/calendars/${props.ownerId}`);
}
catch (reason) {
    notFound.value = reason instanceof ApiError && reason.code === 'not_found';
    error.value = reason instanceof Error ? reason.message : 'Could not load calendar.';
} }
async function book(slot) { try {
    await api(`/calendars/${props.ownerId}/bookings`, { method: 'POST', body: JSON.stringify({ slotStart: slot.start }) });
    await load();
}
catch (reason) {
    if (reason instanceof ApiError && reason.code === 'conflict') {
        await load();
        error.value = 'That slot was just taken. The calendar was refreshed.';
    }
    else
        error.value = reason instanceof Error ? reason.message : 'Could not book slot.';
} }
async function cancel(id) { await api(`/calendars/${props.ownerId}/bookings/${id}`, { method: 'DELETE' }); await load(); }
function displayBookingDate(value) { return `${value.slice(0, 4)}.${value.slice(5, 7)}.${value.slice(8, 10)} ${value.slice(11, 16)}`; }
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
if (__VLS_ctx.notFound) {
    const __VLS_0 = CalendarNotFound;
    // @ts-ignore
    const __VLS_1 = __VLS_asFunctionalComponent1(__VLS_0, new __VLS_0({}));
    const __VLS_2 = __VLS_1({}, ...__VLS_functionalComponentArgsRest(__VLS_1));
    var __VLS_5;
    var __VLS_3;
}
else {
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "space-y-5" },
    });
    /** @type {__VLS_StyleScopedClasses['space-y-5']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.h1, __VLS_intrinsics.h1)({
        ...{ class: "text-2xl font-bold" },
    });
    /** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
    (__VLS_ctx.ownerId);
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
        const __VLS_6 = SlotDayList;
        // @ts-ignore
        const __VLS_7 = __VLS_asFunctionalComponent1(__VLS_6, new __VLS_6({
            ...{ 'onAction': {} },
            slots: (__VLS_ctx.calendar.availableSlots),
            actionLabel: "Book",
        }));
        const __VLS_8 = __VLS_7({
            ...{ 'onAction': {} },
            slots: (__VLS_ctx.calendar.availableSlots),
            actionLabel: "Book",
        }, ...__VLS_functionalComponentArgsRest(__VLS_7));
        let __VLS_11;
        const __VLS_12 = {
            /** @type {typeof __VLS_11.action} */
            onAction: (__VLS_ctx.book),
        };
        var __VLS_9;
        var __VLS_10;
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.h2, __VLS_intrinsics.h2)({
        ...{ class: "text-xl font-semibold" },
    });
    /** @type {__VLS_StyleScopedClasses['text-xl']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
    if (__VLS_ctx.calendar?.myBookings.length) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
            ...{ class: "space-y-2" },
        });
        /** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
        for (const [booking] of __VLS_vFor((__VLS_ctx.calendar.myBookings))) {
            __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
                key: (booking.id),
                ...{ class: "flex justify-between rounded bg-white p-3" },
            });
            /** @type {__VLS_StyleScopedClasses['flex']} */ ;
            /** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
            /** @type {__VLS_StyleScopedClasses['rounded']} */ ;
            /** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
            /** @type {__VLS_StyleScopedClasses['p-3']} */ ;
            (__VLS_ctx.displayBookingDate(booking.start));
            __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
                ...{ onClick: (...[$event]) => {
                        if (!!(__VLS_ctx.notFound))
                            throw 0;
                        if (!(__VLS_ctx.calendar?.myBookings.length))
                            throw 0;
                        return (__VLS_ctx.cancel(booking.id));
                        // @ts-ignore
                        [notFound, ownerId, error, error, calendar, calendar, calendar, calendar, book, displayBookingDate, cancel,];
                    } },
            });
            // @ts-ignore
            [];
        }
    }
    else {
        __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({});
    }
}
// @ts-ignore
[];
const __VLS_export = (await import('vue')).defineComponent({
    __typeProps: {},
});
export default {};
