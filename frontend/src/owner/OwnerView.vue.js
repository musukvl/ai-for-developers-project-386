import { onMounted, ref } from 'vue';
import { api } from '../shared/apiClient';
import SlotDayList from '../shared/SlotDayList.vue';
const props = defineProps();
const calendar = ref();
const error = ref('');
const selectedDay = ref(new Date().toISOString().slice(0, 10));
const startTime = ref('');
const endTime = ref('');
const timeOptions = Array.from({ length: 48 }, (_, index) => {
    const hours = Math.floor(index / 2).toString().padStart(2, '0');
    const minutes = index % 2 === 0 ? '00' : '30';
    return `${hours}:${minutes}`;
});
async function load() { try {
    calendar.value = await api(`/calendars/${props.ownerId}/owner`);
}
catch (reason) {
    error.value = reason instanceof Error ? reason.message : 'Could not load calendar.';
} }
async function add() {
    try {
        await api(`/calendars/${props.ownerId}/availability`, {
            method: 'POST',
            body: JSON.stringify({
                start: `${selectedDay.value}T${startTime.value}:00Z`,
                end: `${selectedDay.value}T${endTime.value}:00Z`,
            }),
        });
        startTime.value = '';
        endTime.value = '';
        await load();
    }
    catch (reason) {
        error.value = reason instanceof Error ? reason.message : 'Could not add availability.';
    }
}
async function remove(slot) { await api(`/calendars/${props.ownerId}/availability/${encodeURIComponent(slot.start)}`, { method: 'DELETE' }); await load(); }
async function cancel(id) { await api(`/calendars/${props.ownerId}/owner/bookings/${id}`, { method: 'DELETE' }); await load(); }
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
        ...{ 'onSelectDay': {} },
        slots: (__VLS_ctx.calendar.availableSlots),
        actionLabel: "Remove",
        allowEmptyDaySelection: true,
    }));
    const __VLS_2 = __VLS_1({
        ...{ 'onAction': {} },
        ...{ 'onSelectDay': {} },
        slots: (__VLS_ctx.calendar.availableSlots),
        actionLabel: "Remove",
        allowEmptyDaySelection: true,
    }, ...__VLS_functionalComponentArgsRest(__VLS_1));
    let __VLS_5;
    const __VLS_6 = {
        /** @type {typeof __VLS_5.action} */
        onAction: (__VLS_ctx.remove),
    };
    const __VLS_7 = {
        /** @type {typeof __VLS_5.selectDay} */
        onSelectDay: (...[$event]) => {
            if (!(__VLS_ctx.calendar))
                throw 0;
            return (__VLS_ctx.selectedDay = $event);
            // @ts-ignore
            [ownerId, ownerId, error, error, calendar, calendar, remove, selectedDay,];
        },
    };
    var __VLS_3;
    var __VLS_4;
}
__VLS_asFunctionalElement1(__VLS_intrinsics.form, __VLS_intrinsics.form)({
    ...{ onSubmit: (__VLS_ctx.add) },
    ...{ class: "flex flex-wrap items-end gap-2 rounded-xl border border-slate-200 bg-white p-4" },
});
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['flex-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['items-end']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
/** @type {__VLS_StyleScopedClasses['p-4']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
    ...{ class: "w-full text-sm text-slate-600" },
});
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.strong, __VLS_intrinsics.strong)({});
(__VLS_ctx.selectedDay);
__VLS_asFunctionalElement1(__VLS_intrinsics.label, __VLS_intrinsics.label)({
    ...{ class: "grid gap-1 text-sm font-medium" },
});
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.select, __VLS_intrinsics.select)({
    value: (__VLS_ctx.startTime),
    required: true,
});
__VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    disabled: true,
    value: "",
});
for (const [time] of __VLS_vFor((__VLS_ctx.timeOptions))) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
        key: (time),
        value: (time),
    });
    (time);
    // @ts-ignore
    [selectedDay, add, startTime, timeOptions,];
}
__VLS_asFunctionalElement1(__VLS_intrinsics.label, __VLS_intrinsics.label)({
    ...{ class: "grid gap-1 text-sm font-medium" },
});
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
__VLS_asFunctionalElement1(__VLS_intrinsics.select, __VLS_intrinsics.select)({
    value: (__VLS_ctx.endTime),
    required: true,
});
__VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
    disabled: true,
    value: "",
});
for (const [time] of __VLS_vFor((__VLS_ctx.timeOptions))) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.option, __VLS_intrinsics.option)({
        key: (time),
        value: (time),
    });
    (time);
    // @ts-ignore
    [timeOptions, endTime,];
}
__VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({});
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
        (__VLS_ctx.displayBookingDate(booking.start));
        (booking.visitorName);
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.calendar?.bookings.length))
                        throw 0;
                    return (__VLS_ctx.cancel(booking.id));
                    // @ts-ignore
                    [calendar, calendar, displayBookingDate, cancel,];
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
