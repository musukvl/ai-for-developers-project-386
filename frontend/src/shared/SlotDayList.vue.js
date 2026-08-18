import { computed, ref, watch } from 'vue';
const props = withDefaults(defineProps(), {
    allowEmptyDaySelection: false,
});
const emit = defineEmits();
const selectedDate = ref('');
const displayedMonth = ref(new Date(Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), 1)));
const today = new Date().toISOString().slice(0, 10);
const slotsByDate = computed(() => props.slots.reduce((groupedSlots, slot) => {
    const dateKey = slot.start.slice(0, 10);
    (groupedSlots[dateKey] ??= []).push(slot);
    return groupedSlots;
}, {}));
const selectedSlots = computed(() => slotsByDate.value[selectedDate.value] ?? []);
const monthLabel = computed(() => new Intl.DateTimeFormat('en', { month: 'long', year: 'numeric', timeZone: 'UTC' }).format(displayedMonth.value));
const calendarDays = computed(() => {
    const year = displayedMonth.value.getUTCFullYear();
    const month = displayedMonth.value.getUTCMonth();
    const firstDay = new Date(Date.UTC(year, month, 1));
    const gridStart = new Date(firstDay);
    gridStart.setUTCDate(1 - ((firstDay.getUTCDay() + 6) % 7));
    return Array.from({ length: 42 }, (_, index) => {
        const date = new Date(gridStart);
        date.setUTCDate(gridStart.getUTCDate() + index);
        const key = date.toISOString().slice(0, 10);
        return {
            key,
            day: date.getUTCDate(),
            isCurrentMonth: date.getUTCMonth() === month,
            isPast: key < today,
            slotCount: slotsByDate.value[key]?.length ?? 0,
        };
    });
});
watch(() => props.slots, (slots) => {
    if (!slots.length) {
        if (props.allowEmptyDaySelection && !selectedDate.value) {
            selectedDate.value = new Date().toISOString().slice(0, 10);
        }
        else if (!props.allowEmptyDaySelection) {
            selectedDate.value = '';
        }
        return;
    }
    if (!slotsByDate.value[selectedDate.value]) {
        selectedDate.value = slots[0].start.slice(0, 10);
        displayedMonth.value = new Date(`${selectedDate.value}T00:00:00Z`);
    }
}, { immediate: true });
function previousMonth() {
    displayedMonth.value = new Date(Date.UTC(displayedMonth.value.getUTCFullYear(), displayedMonth.value.getUTCMonth() - 1, 1));
}
function nextMonth() {
    displayedMonth.value = new Date(Date.UTC(displayedMonth.value.getUTCFullYear(), displayedMonth.value.getUTCMonth() + 1, 1));
}
function selectDay(date) {
    selectedDate.value = date;
    emit('selectDay', date);
}
function displaySelectedDate(value) {
    return new Intl.DateTimeFormat('en', { dateStyle: 'full', timeZone: 'UTC' }).format(new Date(`${value}T00:00:00Z`));
}
function displayTime(value) {
    return new Intl.DateTimeFormat('en', {
        hour: '2-digit',
        minute: '2-digit',
        hourCycle: 'h23',
        timeZone: 'UTC',
    }).format(new Date(value));
}
const __VLS_defaults = {
    allowEmptyDaySelection: false,
};
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
if (__VLS_ctx.slots.length || __VLS_ctx.allowEmptyDaySelection) {
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(18rem,0.75fr)]" },
    });
    /** @type {__VLS_StyleScopedClasses['grid']} */ ;
    /** @type {__VLS_StyleScopedClasses['gap-6']} */ ;
    /** @type {__VLS_StyleScopedClasses['lg:grid-cols-[minmax(0,1.25fr)_minmax(18rem,0.75fr)]']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "rounded-xl border border-slate-200 bg-white p-5 shadow-sm" },
    });
    /** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
    /** @type {__VLS_StyleScopedClasses['border']} */ ;
    /** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
    /** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
    /** @type {__VLS_StyleScopedClasses['p-5']} */ ;
    /** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "mb-5 flex items-center justify-between" },
    });
    /** @type {__VLS_StyleScopedClasses['mb-5']} */ ;
    /** @type {__VLS_StyleScopedClasses['flex']} */ ;
    /** @type {__VLS_StyleScopedClasses['items-center']} */ ;
    /** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
        ...{ class: "text-lg font-semibold" },
    });
    /** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "flex gap-2" },
    });
    /** @type {__VLS_StyleScopedClasses['flex']} */ ;
    /** @type {__VLS_StyleScopedClasses['gap-2']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.previousMonth) },
        ...{ class: "calendar-nav" },
        'aria-label': "Previous month",
    });
    /** @type {__VLS_StyleScopedClasses['calendar-nav']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
        ...{ onClick: (__VLS_ctx.nextMonth) },
        ...{ class: "calendar-nav" },
        'aria-label': "Next month",
    });
    /** @type {__VLS_StyleScopedClasses['calendar-nav']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "mb-4 font-medium" },
    });
    /** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
    (__VLS_ctx.monthLabel);
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "grid grid-cols-7 gap-1 text-center text-xs font-semibold text-slate-500" },
    });
    /** @type {__VLS_StyleScopedClasses['grid']} */ ;
    /** @type {__VLS_StyleScopedClasses['grid-cols-7']} */ ;
    /** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-center']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-xs']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-slate-500']} */ ;
    for (const [day] of __VLS_vFor((['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({
            key: (day),
        });
        (day);
        // @ts-ignore
        [slots, allowEmptyDaySelection, previousMonth, nextMonth, monthLabel,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "mt-2 grid grid-cols-7 gap-1" },
    });
    /** @type {__VLS_StyleScopedClasses['mt-2']} */ ;
    /** @type {__VLS_StyleScopedClasses['grid']} */ ;
    /** @type {__VLS_StyleScopedClasses['grid-cols-7']} */ ;
    /** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
    for (const [day] of __VLS_vFor((__VLS_ctx.calendarDays))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.slots.length || __VLS_ctx.allowEmptyDaySelection))
                        throw 0;
                    return (__VLS_ctx.selectDay(day.key));
                    // @ts-ignore
                    [calendarDays, selectDay,];
                } },
            key: (day.key),
            ...{ class: "calendar-day" },
            ...{ class: ({ 'calendar-day--outside': !day.isCurrentMonth, 'calendar-day--past': day.isPast, 'calendar-day--available': day.slotCount && !day.isPast, 'calendar-day--selected': __VLS_ctx.selectedDate === day.key }) },
            disabled: (day.isPast || (!day.slotCount && !__VLS_ctx.allowEmptyDaySelection)),
            'aria-label': (`${day.key}${day.slotCount ? `, ${day.slotCount} available slots` : ''}`),
        });
        /** @type {__VLS_StyleScopedClasses['calendar-day']} */ ;
        /** @type {__VLS_StyleScopedClasses['calendar-day--outside']} */ ;
        /** @type {__VLS_StyleScopedClasses['calendar-day--past']} */ ;
        /** @type {__VLS_StyleScopedClasses['calendar-day--available']} */ ;
        /** @type {__VLS_StyleScopedClasses['calendar-day--selected']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
        (day.day);
        if (day.slotCount) {
            __VLS_asFunctionalElement1(__VLS_intrinsics.small, __VLS_intrinsics.small)({});
            (day.slotCount);
        }
        // @ts-ignore
        [allowEmptyDaySelection, selectedDate,];
    }
    __VLS_asFunctionalElement1(__VLS_intrinsics.section, __VLS_intrinsics.section)({
        ...{ class: "rounded-xl border border-slate-200 bg-white p-5 shadow-sm" },
    });
    /** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
    /** @type {__VLS_StyleScopedClasses['border']} */ ;
    /** @type {__VLS_StyleScopedClasses['border-slate-200']} */ ;
    /** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
    /** @type {__VLS_StyleScopedClasses['p-5']} */ ;
    /** @type {__VLS_StyleScopedClasses['shadow-sm']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.h3, __VLS_intrinsics.h3)({
        ...{ class: "text-lg font-semibold" },
    });
    /** @type {__VLS_StyleScopedClasses['text-lg']} */ ;
    /** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "mb-4 text-sm text-slate-600" },
    });
    /** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
    (__VLS_ctx.displaySelectedDate(__VLS_ctx.selectedDate));
    __VLS_asFunctionalElement1(__VLS_intrinsics.div, __VLS_intrinsics.div)({
        ...{ class: "space-y-2" },
    });
    /** @type {__VLS_StyleScopedClasses['space-y-2']} */ ;
    for (const [slot] of __VLS_vFor((__VLS_ctx.selectedSlots))) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.button, __VLS_intrinsics.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.slots.length || __VLS_ctx.allowEmptyDaySelection))
                        throw 0;
                    return (__VLS_ctx.emit('action', slot));
                    // @ts-ignore
                    [selectedDate, displaySelectedDate, selectedSlots, emit,];
                } },
            key: (slot.start),
            ...{ class: "slot-action" },
        });
        /** @type {__VLS_StyleScopedClasses['slot-action']} */ ;
        __VLS_asFunctionalElement1(__VLS_intrinsics.span, __VLS_intrinsics.span)({});
        (__VLS_ctx.displayTime(slot.start));
        (__VLS_ctx.displayTime(slot.end));
        __VLS_asFunctionalElement1(__VLS_intrinsics.strong, __VLS_intrinsics.strong)({});
        (__VLS_ctx.actionLabel);
        // @ts-ignore
        [displayTime, displayTime, actionLabel,];
    }
    if (!__VLS_ctx.selectedSlots.length) {
        __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
            ...{ class: "rounded bg-slate-50 p-3 text-sm text-slate-600" },
        });
        /** @type {__VLS_StyleScopedClasses['rounded']} */ ;
        /** @type {__VLS_StyleScopedClasses['bg-slate-50']} */ ;
        /** @type {__VLS_StyleScopedClasses['p-3']} */ ;
        /** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
        /** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
    }
}
else {
    __VLS_asFunctionalElement1(__VLS_intrinsics.p, __VLS_intrinsics.p)({
        ...{ class: "rounded bg-white p-4 text-slate-600" },
    });
    /** @type {__VLS_StyleScopedClasses['rounded']} */ ;
    /** @type {__VLS_StyleScopedClasses['bg-white']} */ ;
    /** @type {__VLS_StyleScopedClasses['p-4']} */ ;
    /** @type {__VLS_StyleScopedClasses['text-slate-600']} */ ;
}
// @ts-ignore
[selectedSlots,];
const __VLS_export = (await import('vue')).defineComponent({
    __typeEmits: {},
    __typeProps: {},
    props: {},
});
export default {};
