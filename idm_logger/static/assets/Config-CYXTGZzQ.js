import{a as g,o as f,f as i,m as v,B as K,l as ve,b as u,p as C,h as x,q as _,t as $,n as me,g as z,s as j,w as h,ag as he,T as Qe,aa as M,ah as $e,D as Je,A as Be,ai as N,F as L,x as U,X as ee,z as Ie,a5 as Q,k as et,a6 as tt,aj as nt,ak as at,al as lt,r as y,v as rt,U as it,N as ot,y as T,d,j as E}from"./index-tCnRO_US.js";import{a as st,s as S}from"./index-BFeo_zXb.js";import{b as ye,R as ne,a as we,f as G,s as I}from"./index-Dnq3oTdE.js";import{a as dt,b as xe,s as k}from"./index-D4NuYL77.js";import{s as J}from"./index-Nt7nN80Z.js";import{s as ut}from"./index-82bus4oH.js";import{s as ct}from"./index-BrR10g_-.js";import{s as pt}from"./index-CvXd1A_Z.js";import"./index-Durd54Lu.js";import"./index-BbpNRWSQ.js";var Ee={name:"PlusIcon",extends:ye};function ft(t){return mt(t)||vt(t)||gt(t)||bt()}function bt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function gt(t,e){if(t){if(typeof t=="string")return ue(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?ue(t,e):void 0}}function vt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function mt(t){if(Array.isArray(t))return ue(t)}function ue(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,l=Array(e);n<e;n++)l[n]=t[n];return l}function ht(t,e,n,l,s,r){return f(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),ft(e[0]||(e[0]=[i("path",{d:"M7.67742 6.32258V0.677419C7.67742 0.497757 7.60605 0.325452 7.47901 0.198411C7.35197 0.0713707 7.17966 0 7 0C6.82034 0 6.64803 0.0713707 6.52099 0.198411C6.39395 0.325452 6.32258 0.497757 6.32258 0.677419V6.32258H0.677419C0.497757 6.32258 0.325452 6.39395 0.198411 6.52099C0.0713707 6.64803 0 6.82034 0 7C0 7.17966 0.0713707 7.35197 0.198411 7.47901C0.325452 7.60605 0.497757 7.67742 0.677419 7.67742H6.32258V13.3226C6.32492 13.5015 6.39704 13.6725 6.52358 13.799C6.65012 13.9255 6.82106 13.9977 7 14C7.17966 14 7.35197 13.9286 7.47901 13.8016C7.60605 13.6745 7.67742 13.5022 7.67742 13.3226V7.67742H13.3226C13.5022 7.67742 13.6745 7.60605 13.8016 7.47901C13.9286 7.35197 14 7.17966 14 7C13.9977 6.82106 13.9255 6.65012 13.799 6.52358C13.6725 6.39704 13.5015 6.32492 13.3226 6.32258H7.67742Z",fill:"currentColor"},null,-1)])),16)}Ee.render=ht;var yt=`
    .p-fieldset {
        background: dt('fieldset.background');
        border: 1px solid dt('fieldset.border.color');
        border-radius: dt('fieldset.border.radius');
        color: dt('fieldset.color');
        padding: dt('fieldset.padding');
        margin: 0;
    }

    .p-fieldset-legend {
        background: dt('fieldset.legend.background');
        border-radius: dt('fieldset.legend.border.radius');
        border-width: dt('fieldset.legend.border.width');
        border-style: solid;
        border-color: dt('fieldset.legend.border.color');
        padding: dt('fieldset.legend.padding');
        transition:
            background dt('fieldset.transition.duration'),
            color dt('fieldset.transition.duration'),
            outline-color dt('fieldset.transition.duration'),
            box-shadow dt('fieldset.transition.duration');
    }

    .p-fieldset-toggleable > .p-fieldset-legend {
        padding: 0;
    }

    .p-fieldset-toggle-button {
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        text-decoration: none;
        display: flex;
        gap: dt('fieldset.legend.gap');
        align-items: center;
        justify-content: center;
        padding: dt('fieldset.legend.padding');
        background: transparent;
        border: 0 none;
        border-radius: dt('fieldset.legend.border.radius');
        transition:
            background dt('fieldset.transition.duration'),
            color dt('fieldset.transition.duration'),
            outline-color dt('fieldset.transition.duration'),
            box-shadow dt('fieldset.transition.duration');
        outline-color: transparent;
    }

    .p-fieldset-legend-label {
        font-weight: dt('fieldset.legend.font.weight');
    }

    .p-fieldset-toggle-button:focus-visible {
        box-shadow: dt('fieldset.legend.focus.ring.shadow');
        outline: dt('fieldset.legend.focus.ring.width') dt('fieldset.legend.focus.ring.style') dt('fieldset.legend.focus.ring.color');
        outline-offset: dt('fieldset.legend.focus.ring.offset');
    }

    .p-fieldset-toggleable > .p-fieldset-legend:hover {
        color: dt('fieldset.legend.hover.color');
        background: dt('fieldset.legend.hover.background');
    }

    .p-fieldset-toggle-icon {
        color: dt('fieldset.toggle.icon.color');
        transition: color dt('fieldset.transition.duration');
    }

    .p-fieldset-toggleable > .p-fieldset-legend:hover .p-fieldset-toggle-icon {
        color: dt('fieldset.toggle.icon.hover.color');
    }

    .p-fieldset-content-container {
        display: grid;
        grid-template-rows: 1fr;
    }

    .p-fieldset-content-wrapper {
        min-height: 0;
    }

    .p-fieldset-content {
        padding: dt('fieldset.content.padding');
    }
`,wt={root:function(e){var n=e.props;return["p-fieldset p-component",{"p-fieldset-toggleable":n.toggleable}]},legend:"p-fieldset-legend",legendLabel:"p-fieldset-legend-label",toggleButton:"p-fieldset-toggle-button",toggleIcon:"p-fieldset-toggle-icon",contentContainer:"p-fieldset-content-container",contentWrapper:"p-fieldset-content-wrapper",content:"p-fieldset-content"},xt=K.extend({name:"fieldset",style:yt,classes:wt}),kt={name:"BaseFieldset",extends:we,props:{legend:String,toggleable:Boolean,collapsed:Boolean,toggleButtonProps:{type:null,default:null}},style:xt,provide:function(){return{$pcFieldset:this,$parentInstance:this}}},A={name:"Fieldset",extends:kt,inheritAttrs:!1,emits:["update:collapsed","toggle"],data:function(){return{d_collapsed:this.collapsed}},watch:{collapsed:function(e){this.d_collapsed=e}},methods:{toggle:function(e){this.d_collapsed=!this.d_collapsed,this.$emit("update:collapsed",this.d_collapsed),this.$emit("toggle",{originalEvent:e,value:this.d_collapsed})},onKeyDown:function(e){(e.code==="Enter"||e.code==="NumpadEnter"||e.code==="Space")&&(this.toggle(e),e.preventDefault())}},computed:{buttonAriaLabel:function(){return this.toggleButtonProps&&this.toggleButtonProps.ariaLabel?this.toggleButtonProps.ariaLabel:this.legend},dataP:function(){return G({toggleable:this.toggleable})}},directives:{ripple:ne},components:{PlusIcon:Ee,MinusIcon:st}};function R(t){"@babel/helpers - typeof";return R=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},R(t)}function Ce(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(t);e&&(l=l.filter(function(s){return Object.getOwnPropertyDescriptor(t,s).enumerable})),n.push.apply(n,l)}return n}function De(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Ce(Object(n),!0).forEach(function(l){Pt(t,l,n[l])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Ce(Object(n)).forEach(function(l){Object.defineProperty(t,l,Object.getOwnPropertyDescriptor(n,l))})}return t}function Pt(t,e,n){return(e=St(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function St(t){var e=Tt(t,"string");return R(e)=="symbol"?e:e+""}function Tt(t,e){if(R(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var l=n.call(t,e);if(R(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Vt=["data-p"],At=["data-p"],$t=["id"],Bt=["id","aria-controls","aria-expanded","aria-label"],It=["id","aria-labelledby"];function Ct(t,e,n,l,s,r){var c=ve("ripple");return f(),g("fieldset",v({class:t.cx("root"),"data-p":r.dataP},t.ptmi("root")),[i("legend",v({class:t.cx("legend"),"data-p":r.dataP},t.ptm("legend")),[C(t.$slots,"legend",{toggleCallback:r.toggle},function(){return[t.toggleable?x("",!0):(f(),g("span",v({key:0,id:t.$id+"_header",class:t.cx("legendLabel")},t.ptm("legendLabel")),$(t.legend),17,$t)),t.toggleable?_((f(),g("button",v({key:1,id:t.$id+"_header",type:"button","aria-controls":t.$id+"_content","aria-expanded":!s.d_collapsed,"aria-label":r.buttonAriaLabel,class:t.cx("toggleButton"),onClick:e[0]||(e[0]=function(){return r.toggle&&r.toggle.apply(r,arguments)}),onKeydown:e[1]||(e[1]=function(){return r.onKeyDown&&r.onKeyDown.apply(r,arguments)})},De(De({},t.toggleButtonProps),t.ptm("toggleButton"))),[C(t.$slots,t.$slots.toggleicon?"toggleicon":"togglericon",{collapsed:s.d_collapsed,class:me(t.cx("toggleIcon"))},function(){return[(f(),z(j(s.d_collapsed?"PlusIcon":"MinusIcon"),v({class:t.cx("toggleIcon")},t.ptm("toggleIcon")),null,16,["class"]))]}),i("span",v({class:t.cx("legendLabel")},t.ptm("legendLabel")),$(t.legend),17)],16,Bt)),[[c]]):x("",!0)]})],16,At),u(Qe,v({name:"p-collapsible"},t.ptm("transition")),{default:h(function(){return[_(i("div",v({id:t.$id+"_content",class:t.cx("contentContainer"),role:"region","aria-labelledby":t.$id+"_header"},t.ptm("contentContainer")),[i("div",v({class:t.cx("contentWrapper")},t.ptm("contentWrapper")),[i("div",v({class:t.cx("content")},t.ptm("content")),[C(t.$slots,"default")],16)],16)],16,It),[[he,!s.d_collapsed]])]}),_:3},16)],16,Vt)}A.render=Ct;var Dt=`
    .p-textarea {
        font-family: inherit;
        font-feature-settings: inherit;
        font-size: 1rem;
        color: dt('textarea.color');
        background: dt('textarea.background');
        padding-block: dt('textarea.padding.y');
        padding-inline: dt('textarea.padding.x');
        border: 1px solid dt('textarea.border.color');
        transition:
            background dt('textarea.transition.duration'),
            color dt('textarea.transition.duration'),
            border-color dt('textarea.transition.duration'),
            outline-color dt('textarea.transition.duration'),
            box-shadow dt('textarea.transition.duration');
        appearance: none;
        border-radius: dt('textarea.border.radius');
        outline-color: transparent;
        box-shadow: dt('textarea.shadow');
    }

    .p-textarea:enabled:hover {
        border-color: dt('textarea.hover.border.color');
    }

    .p-textarea:enabled:focus {
        border-color: dt('textarea.focus.border.color');
        box-shadow: dt('textarea.focus.ring.shadow');
        outline: dt('textarea.focus.ring.width') dt('textarea.focus.ring.style') dt('textarea.focus.ring.color');
        outline-offset: dt('textarea.focus.ring.offset');
    }

    .p-textarea.p-invalid {
        border-color: dt('textarea.invalid.border.color');
    }

    .p-textarea.p-variant-filled {
        background: dt('textarea.filled.background');
    }

    .p-textarea.p-variant-filled:enabled:hover {
        background: dt('textarea.filled.hover.background');
    }

    .p-textarea.p-variant-filled:enabled:focus {
        background: dt('textarea.filled.focus.background');
    }

    .p-textarea:disabled {
        opacity: 1;
        background: dt('textarea.disabled.background');
        color: dt('textarea.disabled.color');
    }

    .p-textarea::placeholder {
        color: dt('textarea.placeholder.color');
    }

    .p-textarea.p-invalid::placeholder {
        color: dt('textarea.invalid.placeholder.color');
    }

    .p-textarea-fluid {
        width: 100%;
    }

    .p-textarea-resizable {
        overflow: hidden;
        resize: none;
    }

    .p-textarea-sm {
        font-size: dt('textarea.sm.font.size');
        padding-block: dt('textarea.sm.padding.y');
        padding-inline: dt('textarea.sm.padding.x');
    }

    .p-textarea-lg {
        font-size: dt('textarea.lg.font.size');
        padding-block: dt('textarea.lg.padding.y');
        padding-inline: dt('textarea.lg.padding.x');
    }
`,Lt={root:function(e){var n=e.instance,l=e.props;return["p-textarea p-component",{"p-filled":n.$filled,"p-textarea-resizable ":l.autoResize,"p-textarea-sm p-inputfield-sm":l.size==="small","p-textarea-lg p-inputfield-lg":l.size==="large","p-invalid":n.$invalid,"p-variant-filled":n.$variant==="filled","p-textarea-fluid":n.$fluid}]}},Et=K.extend({name:"textarea",style:Dt,classes:Lt}),_t={name:"BaseTextarea",extends:dt,props:{autoResize:Boolean},style:Et,provide:function(){return{$pcTextarea:this,$parentInstance:this}}};function W(t){"@babel/helpers - typeof";return W=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},W(t)}function zt(t,e,n){return(e=Ot(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Ot(t){var e=Kt(t,"string");return W(e)=="symbol"?e:e+""}function Kt(t,e){if(W(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var l=n.call(t,e);if(W(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var te={name:"Textarea",extends:_t,inheritAttrs:!1,observer:null,mounted:function(){var e=this;this.autoResize&&(this.observer=new ResizeObserver(function(){requestAnimationFrame(function(){e.resize()})}),this.observer.observe(this.$el))},updated:function(){this.autoResize&&this.resize()},beforeUnmount:function(){this.observer&&this.observer.disconnect()},methods:{resize:function(){if(this.$el.offsetParent){var e=this.$el.style.height,n=parseInt(e)||0,l=this.$el.scrollHeight,s=!n||l>n,r=n&&l<n;r?(this.$el.style.height="auto",this.$el.style.height="".concat(this.$el.scrollHeight,"px")):s&&(this.$el.style.height="".concat(l,"px"))}},onInput:function(e){this.autoResize&&this.resize(),this.writeValue(e.target.value,e)}},computed:{attrs:function(){return v(this.ptmi("root",{context:{filled:this.$filled,disabled:this.disabled}}),this.formField)},dataP:function(){return G(zt({invalid:this.$invalid,fluid:this.$fluid,filled:this.$variant==="filled"},this.size,this.size))}}},jt=["value","name","disabled","aria-invalid","data-p"];function Ut(t,e,n,l,s,r){return f(),g("textarea",v({class:t.cx("root"),value:t.d_value,name:t.name,disabled:t.disabled,"aria-invalid":t.invalid||void 0,"data-p":r.dataP,onInput:e[0]||(e[0]=function(){return r.onInput&&r.onInput.apply(r,arguments)})},r.attrs),null,16,jt)}te.render=Ut;var _e={name:"ChevronLeftIcon",extends:ye};function Ht(t){return Nt(t)||Mt(t)||Ft(t)||qt()}function qt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Ft(t,e){if(t){if(typeof t=="string")return ce(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?ce(t,e):void 0}}function Mt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Nt(t){if(Array.isArray(t))return ce(t)}function ce(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,l=Array(e);n<e;n++)l[n]=t[n];return l}function Rt(t,e,n,l,s,r){return f(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Ht(e[0]||(e[0]=[i("path",{d:"M9.61296 13C9.50997 13.0005 9.40792 12.9804 9.3128 12.9409C9.21767 12.9014 9.13139 12.8433 9.05902 12.7701L3.83313 7.54416C3.68634 7.39718 3.60388 7.19795 3.60388 6.99022C3.60388 6.78249 3.68634 6.58325 3.83313 6.43628L9.05902 1.21039C9.20762 1.07192 9.40416 0.996539 9.60724 1.00012C9.81032 1.00371 10.0041 1.08597 10.1477 1.22959C10.2913 1.37322 10.3736 1.56698 10.3772 1.77005C10.3808 1.97313 10.3054 2.16968 10.1669 2.31827L5.49496 6.99022L10.1669 11.6622C10.3137 11.8091 10.3962 12.0084 10.3962 12.2161C10.3962 12.4238 10.3137 12.6231 10.1669 12.7701C10.0945 12.8433 10.0083 12.9014 9.91313 12.9409C9.81801 12.9804 9.71596 13.0005 9.61296 13Z",fill:"currentColor"},null,-1)])),16)}_e.render=Rt;var ze={name:"ChevronRightIcon",extends:ye};function Wt(t){return Gt(t)||Yt(t)||Xt(t)||Zt()}function Zt(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Xt(t,e){if(t){if(typeof t=="string")return pe(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?pe(t,e):void 0}}function Yt(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Gt(t){if(Array.isArray(t))return pe(t)}function pe(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,l=Array(e);n<e;n++)l[n]=t[n];return l}function Qt(t,e,n,l,s,r){return f(),g("svg",v({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Wt(e[0]||(e[0]=[i("path",{d:"M4.38708 13C4.28408 13.0005 4.18203 12.9804 4.08691 12.9409C3.99178 12.9014 3.9055 12.8433 3.83313 12.7701C3.68634 12.6231 3.60388 12.4238 3.60388 12.2161C3.60388 12.0084 3.68634 11.8091 3.83313 11.6622L8.50507 6.99022L3.83313 2.31827C3.69467 2.16968 3.61928 1.97313 3.62287 1.77005C3.62645 1.56698 3.70872 1.37322 3.85234 1.22959C3.99596 1.08597 4.18972 1.00371 4.3928 1.00012C4.59588 0.996539 4.79242 1.07192 4.94102 1.21039L10.1669 6.43628C10.3137 6.58325 10.3962 6.78249 10.3962 6.99022C10.3962 7.19795 10.3137 7.39718 10.1669 7.54416L4.94102 12.7701C4.86865 12.8433 4.78237 12.9014 4.68724 12.9409C4.59212 12.9804 4.49007 13.0005 4.38708 13Z",fill:"currentColor"},null,-1)])),16)}ze.render=Qt;var Jt=`
    .p-tabview-tablist-container {
        position: relative;
    }

    .p-tabview-scrollable > .p-tabview-tablist-container {
        overflow: hidden;
    }

    .p-tabview-tablist-scroll-container {
        overflow-x: auto;
        overflow-y: hidden;
        scroll-behavior: smooth;
        scrollbar-width: none;
        overscroll-behavior: contain auto;
    }

    .p-tabview-tablist-scroll-container::-webkit-scrollbar {
        display: none;
    }

    .p-tabview-tablist {
        display: flex;
        margin: 0;
        padding: 0;
        list-style-type: none;
        flex: 1 1 auto;
        background: dt('tabview.tab.list.background');
        border: 1px solid dt('tabview.tab.list.border.color');
        border-width: 0 0 1px 0;
        position: relative;
    }

    .p-tabview-tab-header {
        cursor: pointer;
        user-select: none;
        display: flex;
        align-items: center;
        text-decoration: none;
        position: relative;
        overflow: hidden;
        border-style: solid;
        border-width: 0 0 1px 0;
        border-color: transparent transparent dt('tabview.tab.border.color') transparent;
        color: dt('tabview.tab.color');
        padding: 1rem 1.125rem;
        font-weight: 600;
        border-top-right-radius: dt('border.radius.md');
        border-top-left-radius: dt('border.radius.md');
        transition:
            color dt('tabview.transition.duration'),
            outline-color dt('tabview.transition.duration');
        margin: 0 0 -1px 0;
        outline-color: transparent;
    }

    .p-tabview-tablist-item:not(.p-disabled) .p-tabview-tab-header:focus-visible {
        outline: dt('focus.ring.width') dt('focus.ring.style') dt('focus.ring.color');
        outline-offset: -1px;
    }

    .p-tabview-tablist-item:not(.p-highlight):not(.p-disabled):hover > .p-tabview-tab-header {
        color: dt('tabview.tab.hover.color');
    }

    .p-tabview-tablist-item.p-highlight > .p-tabview-tab-header {
        color: dt('tabview.tab.active.color');
    }

    .p-tabview-tab-title {
        line-height: 1;
        white-space: nowrap;
    }

    .p-tabview-next-button,
    .p-tabview-prev-button {
        position: absolute;
        top: 0;
        margin: 0;
        padding: 0;
        z-index: 2;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: dt('tabview.nav.button.background');
        color: dt('tabview.nav.button.color');
        width: 2.5rem;
        border-radius: 0;
        outline-color: transparent;
        transition:
            color dt('tabview.transition.duration'),
            outline-color dt('tabview.transition.duration');
        box-shadow: dt('tabview.nav.button.shadow');
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-tabview-next-button:focus-visible,
    .p-tabview-prev-button:focus-visible {
        outline: dt('focus.ring.width') dt('focus.ring.style') dt('focus.ring.color');
        outline-offset: dt('focus.ring.offset');
    }

    .p-tabview-next-button:hover,
    .p-tabview-prev-button:hover {
        color: dt('tabview.nav.button.hover.color');
    }

    .p-tabview-prev-button {
        left: 0;
    }

    .p-tabview-next-button {
        right: 0;
    }

    .p-tabview-panels {
        background: dt('tabview.tab.panel.background');
        color: dt('tabview.tab.panel.color');
        padding: 0.875rem 1.125rem 1.125rem 1.125rem;
    }

    .p-tabview-ink-bar {
        z-index: 1;
        display: block;
        position: absolute;
        bottom: -1px;
        height: 1px;
        background: dt('tabview.tab.active.border.color');
        transition: 250ms cubic-bezier(0.35, 0, 0.25, 1);
    }
`,en={root:function(e){var n=e.props;return["p-tabview p-component",{"p-tabview-scrollable":n.scrollable}]},navContainer:"p-tabview-tablist-container",prevButton:"p-tabview-prev-button",navContent:"p-tabview-tablist-scroll-container",nav:"p-tabview-tablist",tab:{header:function(e){var n=e.instance,l=e.tab,s=e.index;return["p-tabview-tablist-item",n.getTabProp(l,"headerClass"),{"p-tabview-tablist-item-active":n.d_activeIndex===s,"p-disabled":n.getTabProp(l,"disabled")}]},headerAction:"p-tabview-tab-header",headerTitle:"p-tabview-tab-title",content:function(e){var n=e.instance,l=e.tab;return["p-tabview-panel",n.getTabProp(l,"contentClass")]}},inkbar:"p-tabview-ink-bar",nextButton:"p-tabview-next-button",panelContainer:"p-tabview-panels"},tn=K.extend({name:"tabview",style:Jt,classes:en}),nn={name:"BaseTabView",extends:we,props:{activeIndex:{type:Number,default:0},lazy:{type:Boolean,default:!1},scrollable:{type:Boolean,default:!1},tabindex:{type:Number,default:0},selectOnFocus:{type:Boolean,default:!1},prevButtonProps:{type:null,default:null},nextButtonProps:{type:null,default:null},prevIcon:{type:String,default:void 0},nextIcon:{type:String,default:void 0}},style:tn,provide:function(){return{$pcTabs:void 0,$pcTabView:this,$parentInstance:this}}},Oe={name:"TabView",extends:nn,inheritAttrs:!1,emits:["update:activeIndex","tab-change","tab-click"],data:function(){return{d_activeIndex:this.activeIndex,isPrevButtonDisabled:!0,isNextButtonDisabled:!1}},watch:{activeIndex:function(e){this.d_activeIndex=e,this.scrollInView({index:e})}},mounted:function(){console.warn("Deprecated since v4. Use Tabs component instead."),this.updateInkBar(),this.scrollable&&this.updateButtonState()},updated:function(){this.updateInkBar(),this.scrollable&&this.updateButtonState()},methods:{isTabPanel:function(e){return e.type.name==="TabPanel"},isTabActive:function(e){return this.d_activeIndex===e},getTabProp:function(e,n){return e.props?e.props[n]:void 0},getKey:function(e,n){return this.getTabProp(e,"header")||n},getTabHeaderActionId:function(e){return"".concat(this.$id,"_").concat(e,"_header_action")},getTabContentId:function(e){return"".concat(this.$id,"_").concat(e,"_content")},getTabPT:function(e,n,l){var s=this.tabs.length,r={props:e.props,parent:{instance:this,props:this.$props,state:this.$data},context:{index:l,count:s,first:l===0,last:l===s-1,active:this.isTabActive(l)}};return v(this.ptm("tabpanel.".concat(n),{tabpanel:r}),this.ptm("tabpanel.".concat(n),r),this.ptmo(this.getTabProp(e,"pt"),n,r))},onScroll:function(e){this.scrollable&&this.updateButtonState(),e.preventDefault()},onPrevButtonClick:function(){var e=this.$refs.content,n=M(e),l=e.scrollLeft-n;e.scrollLeft=l<=0?0:l},onNextButtonClick:function(){var e=this.$refs.content,n=M(e)-this.getVisibleButtonWidths(),l=e.scrollLeft+n,s=e.scrollWidth-n;e.scrollLeft=l>=s?s:l},onTabClick:function(e,n,l){this.changeActiveIndex(e,n,l),this.$emit("tab-click",{originalEvent:e,index:l})},onTabKeyDown:function(e,n,l){switch(e.code){case"ArrowLeft":this.onTabArrowLeftKey(e);break;case"ArrowRight":this.onTabArrowRightKey(e);break;case"Home":this.onTabHomeKey(e);break;case"End":this.onTabEndKey(e);break;case"PageDown":this.onPageDownKey(e);break;case"PageUp":this.onPageUpKey(e);break;case"Enter":case"NumpadEnter":case"Space":this.onTabEnterKey(e,n,l);break}},onTabArrowRightKey:function(e){var n=this.findNextHeaderAction(e.target.parentElement);n?this.changeFocusedTab(e,n):this.onTabHomeKey(e),e.preventDefault()},onTabArrowLeftKey:function(e){var n=this.findPrevHeaderAction(e.target.parentElement);n?this.changeFocusedTab(e,n):this.onTabEndKey(e),e.preventDefault()},onTabHomeKey:function(e){var n=this.findFirstHeaderAction();this.changeFocusedTab(e,n),e.preventDefault()},onTabEndKey:function(e){var n=this.findLastHeaderAction();this.changeFocusedTab(e,n),e.preventDefault()},onPageDownKey:function(e){this.scrollInView({index:this.$refs.nav.children.length-2}),e.preventDefault()},onPageUpKey:function(e){this.scrollInView({index:0}),e.preventDefault()},onTabEnterKey:function(e,n,l){this.changeActiveIndex(e,n,l),e.preventDefault()},findNextHeaderAction:function(e){var n=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,l=n?e:e.nextElementSibling;return l?N(l,"data-p-disabled")||N(l,"data-pc-section")==="inkbar"?this.findNextHeaderAction(l):Be(l,'[data-pc-section="headeraction"]'):null},findPrevHeaderAction:function(e){var n=arguments.length>1&&arguments[1]!==void 0?arguments[1]:!1,l=n?e:e.previousElementSibling;return l?N(l,"data-p-disabled")||N(l,"data-pc-section")==="inkbar"?this.findPrevHeaderAction(l):Be(l,'[data-pc-section="headeraction"]'):null},findFirstHeaderAction:function(){return this.findNextHeaderAction(this.$refs.nav.firstElementChild,!0)},findLastHeaderAction:function(){return this.findPrevHeaderAction(this.$refs.nav.lastElementChild,!0)},changeActiveIndex:function(e,n,l){!this.getTabProp(n,"disabled")&&this.d_activeIndex!==l&&(this.d_activeIndex=l,this.$emit("update:activeIndex",l),this.$emit("tab-change",{originalEvent:e,index:l}),this.scrollInView({index:l}))},changeFocusedTab:function(e,n){if(n&&(Je(n),this.scrollInView({element:n}),this.selectOnFocus)){var l=parseInt(n.parentElement.dataset.pcIndex,10),s=this.tabs[l];this.changeActiveIndex(e,s,l)}},scrollInView:function(e){var n=e.element,l=e.index,s=l===void 0?-1:l,r=n||this.$refs.nav.children[s];r&&r.scrollIntoView&&r.scrollIntoView({block:"nearest"})},updateInkBar:function(){var e=this.$refs.nav.children[this.d_activeIndex];this.$refs.inkbar.style.width=M(e)+"px",this.$refs.inkbar.style.left=$e(e).left-$e(this.$refs.nav).left+"px"},updateButtonState:function(){var e=this.$refs.content,n=e.scrollLeft,l=e.scrollWidth,s=M(e);this.isPrevButtonDisabled=n===0,this.isNextButtonDisabled=parseInt(n)===l-s},getVisibleButtonWidths:function(){var e=this.$refs,n=e.prevBtn,l=e.nextBtn;return[n,l].reduce(function(s,r){return r?s+M(r):s},0)}},computed:{tabs:function(){var e=this;return this.$slots.default().reduce(function(n,l){return e.isTabPanel(l)?n.push(l):l.children&&l.children instanceof Array&&l.children.forEach(function(s){e.isTabPanel(s)&&n.push(s)}),n},[])},prevButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.previous:void 0},nextButtonAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.next:void 0}},directives:{ripple:ne},components:{ChevronLeftIcon:_e,ChevronRightIcon:ze}};function Z(t){"@babel/helpers - typeof";return Z=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Z(t)}function Le(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(t);e&&(l=l.filter(function(s){return Object.getOwnPropertyDescriptor(t,s).enumerable})),n.push.apply(n,l)}return n}function V(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?Le(Object(n),!0).forEach(function(l){an(t,l,n[l])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):Le(Object(n)).forEach(function(l){Object.defineProperty(t,l,Object.getOwnPropertyDescriptor(n,l))})}return t}function an(t,e,n){return(e=ln(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function ln(t){var e=rn(t,"string");return Z(e)=="symbol"?e:e+""}function rn(t,e){if(Z(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var l=n.call(t,e);if(Z(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var on=["tabindex","aria-label"],sn=["data-p-active","data-p-disabled","data-pc-index"],dn=["id","tabindex","aria-disabled","aria-selected","aria-controls","onClick","onKeydown"],un=["tabindex","aria-label"],cn=["id","aria-labelledby","data-pc-index","data-p-active"];function pn(t,e,n,l,s,r){var c=ve("ripple");return f(),g("div",v({class:t.cx("root"),role:"tablist"},t.ptmi("root")),[i("div",v({class:t.cx("navContainer")},t.ptm("navContainer")),[t.scrollable&&!s.isPrevButtonDisabled?_((f(),g("button",v({key:0,ref:"prevBtn",type:"button",class:t.cx("prevButton"),tabindex:t.tabindex,"aria-label":r.prevButtonAriaLabel,onClick:e[0]||(e[0]=function(){return r.onPrevButtonClick&&r.onPrevButtonClick.apply(r,arguments)})},V(V({},t.prevButtonProps),t.ptm("prevButton")),{"data-pc-group-section":"navbutton"}),[C(t.$slots,"previcon",{},function(){return[(f(),z(j(t.prevIcon?"span":"ChevronLeftIcon"),v({"aria-hidden":"true",class:t.prevIcon},t.ptm("prevIcon")),null,16,["class"]))]})],16,on)),[[c]]):x("",!0),i("div",v({ref:"content",class:t.cx("navContent"),onScroll:e[1]||(e[1]=function(){return r.onScroll&&r.onScroll.apply(r,arguments)})},t.ptm("navContent")),[i("ul",v({ref:"nav",class:t.cx("nav")},t.ptm("nav")),[(f(!0),g(L,null,U(r.tabs,function(p,m){return f(),g("li",v({key:r.getKey(p,m),style:r.getTabProp(p,"headerStyle"),class:t.cx("tab.header",{tab:p,index:m}),role:"presentation"},{ref_for:!0},V(V(V({},r.getTabProp(p,"headerProps")),r.getTabPT(p,"root",m)),r.getTabPT(p,"header",m)),{"data-pc-name":"tabpanel","data-p-active":s.d_activeIndex===m,"data-p-disabled":r.getTabProp(p,"disabled"),"data-pc-index":m}),[_((f(),g("a",v({id:r.getTabHeaderActionId(m),class:t.cx("tab.headerAction"),tabindex:r.getTabProp(p,"disabled")||!r.isTabActive(m)?-1:t.tabindex,role:"tab","aria-disabled":r.getTabProp(p,"disabled"),"aria-selected":r.isTabActive(m),"aria-controls":r.getTabContentId(m),onClick:function(D){return r.onTabClick(D,p,m)},onKeydown:function(D){return r.onTabKeyDown(D,p,m)}},{ref_for:!0},V(V({},r.getTabProp(p,"headerActionProps")),r.getTabPT(p,"headerAction",m))),[p.props&&p.props.header?(f(),g("span",v({key:0,class:t.cx("tab.headerTitle")},{ref_for:!0},r.getTabPT(p,"headerTitle",m)),$(p.props.header),17)):x("",!0),p.children&&p.children.header?(f(),z(j(p.children.header),{key:1})):x("",!0)],16,dn)),[[c]])],16,sn)}),128)),i("li",v({ref:"inkbar",class:t.cx("inkbar"),role:"presentation","aria-hidden":"true"},t.ptm("inkbar")),null,16)],16)],16),t.scrollable&&!s.isNextButtonDisabled?_((f(),g("button",v({key:1,ref:"nextBtn",type:"button",class:t.cx("nextButton"),tabindex:t.tabindex,"aria-label":r.nextButtonAriaLabel,onClick:e[2]||(e[2]=function(){return r.onNextButtonClick&&r.onNextButtonClick.apply(r,arguments)})},V(V({},t.nextButtonProps),t.ptm("nextButton")),{"data-pc-group-section":"navbutton"}),[C(t.$slots,"nexticon",{},function(){return[(f(),z(j(t.nextIcon?"span":"ChevronRightIcon"),v({"aria-hidden":"true",class:t.nextIcon},t.ptm("nextIcon")),null,16,["class"]))]})],16,un)),[[c]]):x("",!0)],16),i("div",v({class:t.cx("panelContainer")},t.ptm("panelContainer")),[(f(!0),g(L,null,U(r.tabs,function(p,m){return f(),g(L,{key:r.getKey(p,m)},[!t.lazy||r.isTabActive(m)?_((f(),g("div",v({key:0,id:r.getTabContentId(m),style:r.getTabProp(p,"contentStyle"),class:t.cx("tab.content",{tab:p}),role:"tabpanel","aria-labelledby":r.getTabHeaderActionId(m)},{ref_for:!0},V(V(V({},r.getTabProp(p,"contentProps")),r.getTabPT(p,"root",m)),r.getTabPT(p,"content",m)),{"data-pc-name":"tabpanel","data-pc-index":m,"data-p-active":s.d_activeIndex===m}),[(f(),z(j(p)))],16,cn)),[[he,t.lazy?!0:r.isTabActive(m)]]):x("",!0)],64)}),128))],16)],16)}Oe.render=pn;var fn={root:function(e){var n=e.instance;return["p-tabpanel",{"p-tabpanel-active":n.active}]}},bn=K.extend({name:"tabpanel",classes:fn}),gn={name:"BaseTabPanel",extends:we,props:{value:{type:[String,Number],default:void 0},as:{type:[String,Object],default:"DIV"},asChild:{type:Boolean,default:!1},header:null,headerStyle:null,headerClass:null,headerProps:null,headerActionProps:null,contentStyle:null,contentClass:null,contentProps:null,disabled:Boolean},style:bn,provide:function(){return{$pcTabPanel:this,$parentInstance:this}}},O={name:"TabPanel",extends:gn,inheritAttrs:!1,inject:["$pcTabs"],computed:{active:function(){var e;return ee((e=this.$pcTabs)===null||e===void 0?void 0:e.d_value,this.value)},id:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tabpanel_").concat(this.value)},ariaLabelledby:function(){var e;return"".concat((e=this.$pcTabs)===null||e===void 0?void 0:e.$id,"_tab_").concat(this.value)},attrs:function(){return v(this.a11yAttrs,this.ptmi("root",this.ptParams))},a11yAttrs:function(){var e;return{id:this.id,tabindex:(e=this.$pcTabs)===null||e===void 0?void 0:e.tabindex,role:"tabpanel","aria-labelledby":this.ariaLabelledby,"data-pc-name":"tabpanel","data-p-active":this.active}},ptParams:function(){return{context:{active:this.active}}}}};function vn(t,e,n,l,s,r){var c,p;return r.$pcTabs?(f(),g(L,{key:1},[t.asChild?C(t.$slots,"default",{key:1,class:me(t.cx("root")),active:r.active,a11yAttrs:r.a11yAttrs}):(f(),g(L,{key:0},[!((c=r.$pcTabs)!==null&&c!==void 0&&c.lazy)||r.active?_((f(),z(j(t.as),v({key:0,class:t.cx("root")},r.attrs),{default:h(function(){return[C(t.$slots,"default")]}),_:3},16,["class"])),[[he,(p=r.$pcTabs)!==null&&p!==void 0&&p.lazy?!0:r.active]]):x("",!0)],64))],64)):C(t.$slots,"default",{key:0})}O.render=vn;var mn=`
    .p-togglebutton {
        display: inline-flex;
        cursor: pointer;
        user-select: none;
        overflow: hidden;
        position: relative;
        color: dt('togglebutton.color');
        background: dt('togglebutton.background');
        border: 1px solid dt('togglebutton.border.color');
        padding: dt('togglebutton.padding');
        font-size: 1rem;
        font-family: inherit;
        font-feature-settings: inherit;
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
        border-radius: dt('togglebutton.border.radius');
        outline-color: transparent;
        font-weight: dt('togglebutton.font.weight');
    }

    .p-togglebutton-content {
        display: inline-flex;
        flex: 1 1 auto;
        align-items: center;
        justify-content: center;
        gap: dt('togglebutton.gap');
        padding: dt('togglebutton.content.padding');
        background: transparent;
        border-radius: dt('togglebutton.content.border.radius');
        transition:
            background dt('togglebutton.transition.duration'),
            color dt('togglebutton.transition.duration'),
            border-color dt('togglebutton.transition.duration'),
            outline-color dt('togglebutton.transition.duration'),
            box-shadow dt('togglebutton.transition.duration');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover {
        background: dt('togglebutton.hover.background');
        color: dt('togglebutton.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked {
        background: dt('togglebutton.checked.background');
        border-color: dt('togglebutton.checked.border.color');
        color: dt('togglebutton.checked.color');
    }

    .p-togglebutton-checked .p-togglebutton-content {
        background: dt('togglebutton.content.checked.background');
        box-shadow: dt('togglebutton.content.checked.shadow');
    }

    .p-togglebutton:focus-visible {
        box-shadow: dt('togglebutton.focus.ring.shadow');
        outline: dt('togglebutton.focus.ring.width') dt('togglebutton.focus.ring.style') dt('togglebutton.focus.ring.color');
        outline-offset: dt('togglebutton.focus.ring.offset');
    }

    .p-togglebutton.p-invalid {
        border-color: dt('togglebutton.invalid.border.color');
    }

    .p-togglebutton:disabled {
        opacity: 1;
        cursor: default;
        background: dt('togglebutton.disabled.background');
        border-color: dt('togglebutton.disabled.border.color');
        color: dt('togglebutton.disabled.color');
    }

    .p-togglebutton-label,
    .p-togglebutton-icon {
        position: relative;
        transition: none;
    }

    .p-togglebutton-icon {
        color: dt('togglebutton.icon.color');
    }

    .p-togglebutton:not(:disabled):not(.p-togglebutton-checked):hover .p-togglebutton-icon {
        color: dt('togglebutton.icon.hover.color');
    }

    .p-togglebutton.p-togglebutton-checked .p-togglebutton-icon {
        color: dt('togglebutton.icon.checked.color');
    }

    .p-togglebutton:disabled .p-togglebutton-icon {
        color: dt('togglebutton.icon.disabled.color');
    }

    .p-togglebutton-sm {
        padding: dt('togglebutton.sm.padding');
        font-size: dt('togglebutton.sm.font.size');
    }

    .p-togglebutton-sm .p-togglebutton-content {
        padding: dt('togglebutton.content.sm.padding');
    }

    .p-togglebutton-lg {
        padding: dt('togglebutton.lg.padding');
        font-size: dt('togglebutton.lg.font.size');
    }

    .p-togglebutton-lg .p-togglebutton-content {
        padding: dt('togglebutton.content.lg.padding');
    }

    .p-togglebutton-fluid {
        width: 100%;
    }
`,hn={root:function(e){var n=e.instance,l=e.props;return["p-togglebutton p-component",{"p-togglebutton-checked":n.active,"p-invalid":n.$invalid,"p-togglebutton-fluid":l.fluid,"p-togglebutton-sm p-inputfield-sm":l.size==="small","p-togglebutton-lg p-inputfield-lg":l.size==="large"}]},content:"p-togglebutton-content",icon:"p-togglebutton-icon",label:"p-togglebutton-label"},yn=K.extend({name:"togglebutton",style:mn,classes:hn}),wn={name:"BaseToggleButton",extends:xe,props:{onIcon:String,offIcon:String,onLabel:{type:String,default:"Yes"},offLabel:{type:String,default:"No"},readonly:{type:Boolean,default:!1},tabindex:{type:Number,default:null},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:yn,provide:function(){return{$pcToggleButton:this,$parentInstance:this}}};function X(t){"@babel/helpers - typeof";return X=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},X(t)}function xn(t,e,n){return(e=kn(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function kn(t){var e=Pn(t,"string");return X(e)=="symbol"?e:e+""}function Pn(t,e){if(X(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var l=n.call(t,e);if(X(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var Ke={name:"ToggleButton",extends:wn,inheritAttrs:!1,emits:["change"],methods:{getPTOptions:function(e){var n=e==="root"?this.ptmi:this.ptm;return n(e,{context:{active:this.active,disabled:this.disabled}})},onChange:function(e){!this.disabled&&!this.readonly&&(this.writeValue(!this.d_value,e),this.$emit("change",e))},onBlur:function(e){var n,l;(n=(l=this.formField).onBlur)===null||n===void 0||n.call(l,e)}},computed:{active:function(){return this.d_value===!0},hasLabel:function(){return Ie(this.onLabel)&&Ie(this.offLabel)},label:function(){return this.hasLabel?this.d_value?this.onLabel:this.offLabel:" "},dataP:function(){return G(xn({checked:this.active,invalid:this.$invalid},this.size,this.size))}},directives:{ripple:ne}},Sn=["tabindex","disabled","aria-pressed","aria-label","aria-labelledby","data-p-checked","data-p-disabled","data-p"],Tn=["data-p"];function Vn(t,e,n,l,s,r){var c=ve("ripple");return _((f(),g("button",v({type:"button",class:t.cx("root"),tabindex:t.tabindex,disabled:t.disabled,"aria-pressed":t.d_value,onClick:e[0]||(e[0]=function(){return r.onChange&&r.onChange.apply(r,arguments)}),onBlur:e[1]||(e[1]=function(){return r.onBlur&&r.onBlur.apply(r,arguments)})},r.getPTOptions("root"),{"aria-label":t.ariaLabel,"aria-labelledby":t.ariaLabelledby,"data-p-checked":r.active,"data-p-disabled":t.disabled,"data-p":r.dataP}),[i("span",v({class:t.cx("content")},r.getPTOptions("content"),{"data-p":r.dataP}),[C(t.$slots,"default",{},function(){return[C(t.$slots,"icon",{value:t.d_value,class:me(t.cx("icon"))},function(){return[t.onIcon||t.offIcon?(f(),g("span",v({key:0,class:[t.cx("icon"),t.d_value?t.onIcon:t.offIcon]},r.getPTOptions("icon")),null,16)):x("",!0)]}),i("span",v({class:t.cx("label")},r.getPTOptions("label")),$(r.label),17)]})],16,Tn)],16,Sn)),[[c]])}Ke.render=Vn;var An=`
    .p-selectbutton {
        display: inline-flex;
        user-select: none;
        vertical-align: bottom;
        outline-color: transparent;
        border-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton {
        border-radius: 0;
        border-width: 1px 1px 1px 0;
    }

    .p-selectbutton .p-togglebutton:focus-visible {
        position: relative;
        z-index: 1;
    }

    .p-selectbutton .p-togglebutton:first-child {
        border-inline-start-width: 1px;
        border-start-start-radius: dt('selectbutton.border.radius');
        border-end-start-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton .p-togglebutton:last-child {
        border-start-end-radius: dt('selectbutton.border.radius');
        border-end-end-radius: dt('selectbutton.border.radius');
    }

    .p-selectbutton.p-invalid {
        outline: 1px solid dt('selectbutton.invalid.border.color');
        outline-offset: 0;
    }

    .p-selectbutton-fluid {
        width: 100%;
    }

    .p-selectbutton-fluid .p-togglebutton {
        flex: 1 1 0;
    }
`,$n={root:function(e){var n=e.props,l=e.instance;return["p-selectbutton p-component",{"p-invalid":l.$invalid,"p-selectbutton-fluid":n.fluid}]}},Bn=K.extend({name:"selectbutton",style:An,classes:$n}),In={name:"BaseSelectButton",extends:xe,props:{options:Array,optionLabel:null,optionValue:null,optionDisabled:null,multiple:Boolean,allowEmpty:{type:Boolean,default:!0},dataKey:null,ariaLabelledby:{type:String,default:null},size:{type:String,default:null},fluid:{type:Boolean,default:null}},style:Bn,provide:function(){return{$pcSelectButton:this,$parentInstance:this}}};function Cn(t,e){var n=typeof Symbol<"u"&&t[Symbol.iterator]||t["@@iterator"];if(!n){if(Array.isArray(t)||(n=je(t))||e){n&&(t=n);var l=0,s=function(){};return{s,n:function(){return l>=t.length?{done:!0}:{done:!1,value:t[l++]}},e:function(P){throw P},f:s}}throw new TypeError(`Invalid attempt to iterate non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}var r,c=!0,p=!1;return{s:function(){n=n.call(t)},n:function(){var P=n.next();return c=P.done,P},e:function(P){p=!0,r=P},f:function(){try{c||n.return==null||n.return()}finally{if(p)throw r}}}}function Dn(t){return _n(t)||En(t)||je(t)||Ln()}function Ln(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function je(t,e){if(t){if(typeof t=="string")return fe(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?fe(t,e):void 0}}function En(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function _n(t){if(Array.isArray(t))return fe(t)}function fe(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,l=Array(e);n<e;n++)l[n]=t[n];return l}var be={name:"SelectButton",extends:In,inheritAttrs:!1,emits:["change"],methods:{getOptionLabel:function(e){return this.optionLabel?Q(e,this.optionLabel):e},getOptionValue:function(e){return this.optionValue?Q(e,this.optionValue):e},getOptionRenderKey:function(e){return this.dataKey?Q(e,this.dataKey):this.getOptionLabel(e)},isOptionDisabled:function(e){return this.optionDisabled?Q(e,this.optionDisabled):!1},isOptionReadonly:function(e){if(this.allowEmpty)return!1;var n=this.isSelected(e);return this.multiple?n&&this.d_value.length===1:n},onOptionSelect:function(e,n,l){var s=this;if(!(this.disabled||this.isOptionDisabled(n)||this.isOptionReadonly(n))){var r=this.isSelected(n),c=this.getOptionValue(n),p;if(this.multiple)if(r){if(p=this.d_value.filter(function(m){return!ee(m,c,s.equalityKey)}),!this.allowEmpty&&p.length===0)return}else p=this.d_value?[].concat(Dn(this.d_value),[c]):[c];else{if(r&&!this.allowEmpty)return;p=r?null:c}this.writeValue(p,e),this.$emit("change",{originalEvent:e,value:p})}},isSelected:function(e){var n=!1,l=this.getOptionValue(e);if(this.multiple){if(this.d_value){var s=Cn(this.d_value),r;try{for(s.s();!(r=s.n()).done;){var c=r.value;if(ee(c,l,this.equalityKey)){n=!0;break}}}catch(p){s.e(p)}finally{s.f()}}}else n=ee(this.d_value,l,this.equalityKey);return n}},computed:{equalityKey:function(){return this.optionValue?null:this.dataKey},dataP:function(){return G({invalid:this.$invalid})}},directives:{ripple:ne},components:{ToggleButton:Ke}},zn=["aria-labelledby","data-p"];function On(t,e,n,l,s,r){var c=et("ToggleButton");return f(),g("div",v({class:t.cx("root"),role:"group","aria-labelledby":t.ariaLabelledby},t.ptmi("root"),{"data-p":r.dataP}),[(f(!0),g(L,null,U(t.options,function(p,m){return f(),z(c,{key:r.getOptionRenderKey(p),modelValue:r.isSelected(p),onLabel:r.getOptionLabel(p),offLabel:r.getOptionLabel(p),disabled:t.disabled||r.isOptionDisabled(p),unstyled:t.unstyled,size:t.size,readonly:r.isOptionReadonly(p),onChange:function(D){return r.onOptionSelect(D,p,m)},pt:t.ptm("pcToggleButton")},tt({_:2},[t.$slots.option?{name:"default",fn:h(function(){return[C(t.$slots,"option",{option:p,index:m},function(){return[i("span",v({ref_for:!0},t.ptm("pcToggleButton").label),$(r.getOptionLabel(p)),17)]})]}),key:"0"}:void 0]),1032,["modelValue","onLabel","offLabel","disabled","unstyled","size","readonly","onChange","pt"])}),128))],16,zn)}be.render=On;var Kn=`
    .p-slider {
        display: block;
        position: relative;
        background: dt('slider.track.background');
        border-radius: dt('slider.track.border.radius');
    }

    .p-slider-handle {
        cursor: grab;
        touch-action: none;
        user-select: none;
        display: flex;
        justify-content: center;
        align-items: center;
        height: dt('slider.handle.height');
        width: dt('slider.handle.width');
        background: dt('slider.handle.background');
        border-radius: dt('slider.handle.border.radius');
        transition:
            background dt('slider.transition.duration'),
            color dt('slider.transition.duration'),
            border-color dt('slider.transition.duration'),
            box-shadow dt('slider.transition.duration'),
            outline-color dt('slider.transition.duration');
        outline-color: transparent;
    }

    .p-slider-handle::before {
        content: '';
        width: dt('slider.handle.content.width');
        height: dt('slider.handle.content.height');
        display: block;
        background: dt('slider.handle.content.background');
        border-radius: dt('slider.handle.content.border.radius');
        box-shadow: dt('slider.handle.content.shadow');
        transition: background dt('slider.transition.duration');
    }

    .p-slider:not(.p-disabled) .p-slider-handle:hover {
        background: dt('slider.handle.hover.background');
    }

    .p-slider:not(.p-disabled) .p-slider-handle:hover::before {
        background: dt('slider.handle.content.hover.background');
    }

    .p-slider-handle:focus-visible {
        box-shadow: dt('slider.handle.focus.ring.shadow');
        outline: dt('slider.handle.focus.ring.width') dt('slider.handle.focus.ring.style') dt('slider.handle.focus.ring.color');
        outline-offset: dt('slider.handle.focus.ring.offset');
    }

    .p-slider-range {
        display: block;
        background: dt('slider.range.background');
        border-radius: dt('slider.track.border.radius');
    }

    .p-slider.p-slider-horizontal {
        height: dt('slider.track.size');
    }

    .p-slider-horizontal .p-slider-range {
        inset-block-start: 0;
        inset-inline-start: 0;
        height: 100%;
    }

    .p-slider-horizontal .p-slider-handle {
        inset-block-start: 50%;
        margin-block-start: calc(-1 * calc(dt('slider.handle.height') / 2));
        margin-inline-start: calc(-1 * calc(dt('slider.handle.width') / 2));
    }

    .p-slider-vertical {
        min-height: 100px;
        width: dt('slider.track.size');
    }

    .p-slider-vertical .p-slider-handle {
        inset-inline-start: 50%;
        margin-inline-start: calc(-1 * calc(dt('slider.handle.width') / 2));
        margin-block-end: calc(-1 * calc(dt('slider.handle.height') / 2));
    }

    .p-slider-vertical .p-slider-range {
        inset-block-end: 0;
        inset-inline-start: 0;
        width: 100%;
    }
`,jn={handle:{position:"absolute"},range:{position:"absolute"}},Un={root:function(e){var n=e.instance,l=e.props;return["p-slider p-component",{"p-disabled":l.disabled,"p-invalid":n.$invalid,"p-slider-horizontal":l.orientation==="horizontal","p-slider-vertical":l.orientation==="vertical"}]},range:"p-slider-range",handle:"p-slider-handle"},Hn=K.extend({name:"slider",style:Kn,classes:Un,inlineStyles:jn}),qn={name:"BaseSlider",extends:xe,props:{min:{type:Number,default:0},max:{type:Number,default:100},orientation:{type:String,default:"horizontal"},step:{type:Number,default:null},range:{type:Boolean,default:!1},tabindex:{type:Number,default:0},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:Hn,provide:function(){return{$pcSlider:this,$parentInstance:this}}};function Y(t){"@babel/helpers - typeof";return Y=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},Y(t)}function Fn(t,e,n){return(e=Mn(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Mn(t){var e=Nn(t,"string");return Y(e)=="symbol"?e:e+""}function Nn(t,e){if(Y(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var l=n.call(t,e);if(Y(l)!="object")return l;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}function Rn(t){return Yn(t)||Xn(t)||Zn(t)||Wn()}function Wn(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Zn(t,e){if(t){if(typeof t=="string")return ge(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?ge(t,e):void 0}}function Xn(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Yn(t){if(Array.isArray(t))return ge(t)}function ge(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,l=Array(e);n<e;n++)l[n]=t[n];return l}var Ue={name:"Slider",extends:qn,inheritAttrs:!1,emits:["change","slideend"],dragging:!1,handleIndex:null,initX:null,initY:null,barWidth:null,barHeight:null,dragListener:null,dragEndListener:null,beforeUnmount:function(){this.unbindDragListeners()},methods:{updateDomData:function(){var e=this.$el.getBoundingClientRect();this.initX=e.left+at(),this.initY=e.top+lt(),this.barWidth=this.$el.offsetWidth,this.barHeight=this.$el.offsetHeight},setValue:function(e){var n,l=e.touches?e.touches[0].pageX:e.pageX,s=e.touches?e.touches[0].pageY:e.pageY;this.orientation==="horizontal"?nt(this.$el)?n=(this.initX+this.barWidth-l)*100/this.barWidth:n=(l-this.initX)*100/this.barWidth:n=(this.initY+this.barHeight-s)*100/this.barHeight;var r=(this.max-this.min)*(n/100)+this.min;if(this.step){var c=this.range?this.value[this.handleIndex]:this.value,p=r-c;p<0?r=c+Math.ceil(r/this.step-c/this.step)*this.step:p>0&&(r=c+Math.floor(r/this.step-c/this.step)*this.step)}else r=Math.floor(r);this.updateModel(e,r)},updateModel:function(e,n){var l=Math.round(n*100)/100,s;this.range?(s=this.value?Rn(this.value):[],this.handleIndex==0?(l<this.min?l=this.min:l>=this.max&&(l=this.max),s[0]=l):(l>this.max?l=this.max:l<=this.min&&(l=this.min),s[1]=l)):(l<this.min?l=this.min:l>this.max&&(l=this.max),s=l),this.writeValue(s,e),this.$emit("change",s)},onDragStart:function(e,n){this.disabled||(this.$el.setAttribute("data-p-sliding",!0),this.dragging=!0,this.updateDomData(),this.range&&this.value[0]===this.max?this.handleIndex=0:this.handleIndex=n,e.currentTarget.focus())},onDrag:function(e){this.dragging&&this.setValue(e)},onDragEnd:function(e){this.dragging&&(this.dragging=!1,this.$el.setAttribute("data-p-sliding",!1),this.$emit("slideend",{originalEvent:e,value:this.value}))},onBarClick:function(e){this.disabled||N(e.target,"data-pc-section")!=="handle"&&(this.updateDomData(),this.setValue(e))},onMouseDown:function(e,n){this.bindDragListeners(),this.onDragStart(e,n)},onKeyDown:function(e,n){switch(this.handleIndex=n,e.code){case"ArrowDown":case"ArrowLeft":this.decrementValue(e,n),e.preventDefault();break;case"ArrowUp":case"ArrowRight":this.incrementValue(e,n),e.preventDefault();break;case"PageDown":this.decrementValue(e,n,!0),e.preventDefault();break;case"PageUp":this.incrementValue(e,n,!0),e.preventDefault();break;case"Home":this.updateModel(e,this.min),e.preventDefault();break;case"End":this.updateModel(e,this.max),e.preventDefault();break}},onBlur:function(e,n){var l,s;(l=(s=this.formField).onBlur)===null||l===void 0||l.call(s,e)},decrementValue:function(e,n){var l=arguments.length>2&&arguments[2]!==void 0?arguments[2]:!1,s;this.range?this.step?s=this.value[n]-this.step:s=this.value[n]-1:this.step?s=this.value-this.step:!this.step&&l?s=this.value-10:s=this.value-1,this.updateModel(e,s),e.preventDefault()},incrementValue:function(e,n){var l=arguments.length>2&&arguments[2]!==void 0?arguments[2]:!1,s;this.range?this.step?s=this.value[n]+this.step:s=this.value[n]+1:this.step?s=this.value+this.step:!this.step&&l?s=this.value+10:s=this.value+1,this.updateModel(e,s),e.preventDefault()},bindDragListeners:function(){this.dragListener||(this.dragListener=this.onDrag.bind(this),document.addEventListener("mousemove",this.dragListener)),this.dragEndListener||(this.dragEndListener=this.onDragEnd.bind(this),document.addEventListener("mouseup",this.dragEndListener))},unbindDragListeners:function(){this.dragListener&&(document.removeEventListener("mousemove",this.dragListener),this.dragListener=null),this.dragEndListener&&(document.removeEventListener("mouseup",this.dragEndListener),this.dragEndListener=null)},rangeStyle:function(){if(this.range){var e=this.rangeEndPosition>this.rangeStartPosition?this.rangeEndPosition-this.rangeStartPosition:this.rangeStartPosition-this.rangeEndPosition,n=this.rangeEndPosition>this.rangeStartPosition?this.rangeStartPosition:this.rangeEndPosition;return this.horizontal?{"inset-inline-start":n+"%",width:e+"%"}:{bottom:n+"%",height:e+"%"}}else return this.horizontal?{width:this.handlePosition+"%"}:{height:this.handlePosition+"%"}},handleStyle:function(){return this.horizontal?{"inset-inline-start":this.handlePosition+"%"}:{bottom:this.handlePosition+"%"}},rangeStartHandleStyle:function(){return this.horizontal?{"inset-inline-start":this.rangeStartPosition+"%"}:{bottom:this.rangeStartPosition+"%"}},rangeEndHandleStyle:function(){return this.horizontal?{"inset-inline-start":this.rangeEndPosition+"%"}:{bottom:this.rangeEndPosition+"%"}}},computed:{value:function(){var e;if(this.range){var n,l,s,r;return[(n=(l=this.d_value)===null||l===void 0?void 0:l[0])!==null&&n!==void 0?n:this.min,(s=(r=this.d_value)===null||r===void 0?void 0:r[1])!==null&&s!==void 0?s:this.max]}return(e=this.d_value)!==null&&e!==void 0?e:this.min},horizontal:function(){return this.orientation==="horizontal"},vertical:function(){return this.orientation==="vertical"},handlePosition:function(){return this.value<this.min?0:this.value>this.max?100:(this.value-this.min)*100/(this.max-this.min)},rangeStartPosition:function(){return this.value&&this.value[0]!==void 0?this.value[0]<this.min?0:(this.value[0]-this.min)*100/(this.max-this.min):0},rangeEndPosition:function(){return this.value&&this.value.length===2&&this.value[1]!==void 0?this.value[1]>this.max?100:(this.value[1]-this.min)*100/(this.max-this.min):100},dataP:function(){return G(Fn({},this.orientation,this.orientation))}}},Gn=["data-p"],Qn=["data-p"],Jn=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"],ea=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"],ta=["tabindex","aria-valuemin","aria-valuenow","aria-valuemax","aria-labelledby","aria-label","aria-orientation","data-p"];function na(t,e,n,l,s,r){return f(),g("div",v({class:t.cx("root"),onClick:e[18]||(e[18]=function(){return r.onBarClick&&r.onBarClick.apply(r,arguments)})},t.ptmi("root"),{"data-p-sliding":!1,"data-p":r.dataP}),[i("span",v({class:t.cx("range"),style:[t.sx("range"),r.rangeStyle()]},t.ptm("range"),{"data-p":r.dataP}),null,16,Qn),t.range?x("",!0):(f(),g("span",v({key:0,class:t.cx("handle"),style:[t.sx("handle"),r.handleStyle()],onTouchstartPassive:e[0]||(e[0]=function(c){return r.onDragStart(c)}),onTouchmovePassive:e[1]||(e[1]=function(c){return r.onDrag(c)}),onTouchend:e[2]||(e[2]=function(c){return r.onDragEnd(c)}),onMousedown:e[3]||(e[3]=function(c){return r.onMouseDown(c)}),onKeydown:e[4]||(e[4]=function(c){return r.onKeyDown(c)}),onBlur:e[5]||(e[5]=function(c){return r.onBlur(c)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("handle"),{"data-p":r.dataP}),null,16,Jn)),t.range?(f(),g("span",v({key:1,class:t.cx("handle"),style:[t.sx("handle"),r.rangeStartHandleStyle()],onTouchstartPassive:e[6]||(e[6]=function(c){return r.onDragStart(c,0)}),onTouchmovePassive:e[7]||(e[7]=function(c){return r.onDrag(c)}),onTouchend:e[8]||(e[8]=function(c){return r.onDragEnd(c)}),onMousedown:e[9]||(e[9]=function(c){return r.onMouseDown(c,0)}),onKeydown:e[10]||(e[10]=function(c){return r.onKeyDown(c,0)}),onBlur:e[11]||(e[11]=function(c){return r.onBlur(c,0)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value?t.d_value[0]:null,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("startHandler"),{"data-p":r.dataP}),null,16,ea)):x("",!0),t.range?(f(),g("span",v({key:2,class:t.cx("handle"),style:[t.sx("handle"),r.rangeEndHandleStyle()],onTouchstartPassive:e[12]||(e[12]=function(c){return r.onDragStart(c,1)}),onTouchmovePassive:e[13]||(e[13]=function(c){return r.onDrag(c)}),onTouchend:e[14]||(e[14]=function(c){return r.onDragEnd(c)}),onMousedown:e[15]||(e[15]=function(c){return r.onMouseDown(c,1)}),onKeydown:e[16]||(e[16]=function(c){return r.onKeyDown(c,1)}),onBlur:e[17]||(e[17]=function(c){return r.onBlur(c,1)}),tabindex:t.tabindex,role:"slider","aria-valuemin":t.min,"aria-valuenow":t.d_value?t.d_value[1]:null,"aria-valuemax":t.max,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,"aria-orientation":t.orientation},t.ptm("endHandler"),{"data-p":r.dataP}),null,16,ta)):x("",!0)],16,Gn)}Ue.render=na;const aa={class:"p-4 flex flex-col gap-4"},la={key:0,class:"flex justify-center"},ra={key:1},ia={class:"flex flex-col gap-6"},oa={class:"flex flex-col gap-4"},sa={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},da={class:"flex flex-col gap-2"},ua={class:"flex flex-col gap-2"},ca={class:"flex flex-col gap-2"},pa={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},fa={class:"flex items-center gap-2"},ba=["for"],ga={class:"flex flex-col gap-2"},va={class:"flex flex-wrap gap-4 p-3 border border-gray-700 rounded bg-gray-900/50"},ma=["for"],ha={class:"flex flex-col gap-4"},ya={class:"flex flex-col gap-2"},wa={class:"flex flex-col gap-4"},xa={class:"flex items-center gap-2 p-3 bg-gray-800 rounded border border-gray-700"},ka={key:0,class:"flex flex-col gap-2"},Pa={class:"flex items-center gap-2"},Sa={key:0,class:"flex flex-col gap-6 mt-4"},Ta={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Va={class:"flex flex-col gap-2"},Aa={class:"flex flex-col gap-2"},$a={class:"flex flex-col gap-2"},Ba={class:"flex flex-col gap-2"},Ia={class:"grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-gray-700 pt-4"},Ca={class:"flex flex-col gap-2"},Da={class:"flex flex-col gap-2"},La={class:"flex flex-col gap-3 border border-green-600/50 rounded bg-green-900/10 p-4"},Ea={class:"flex items-center gap-2"},_a={key:0,class:"ml-8"},za={key:1,class:"text-gray-400 italic"},Oa={class:"flex flex-col gap-6"},Ka={class:"flex items-center gap-2"},ja={key:0,class:"flex flex-col gap-4"},Ua={class:"flex flex-col gap-2"},Ha={class:"flex flex-col gap-2"},qa={class:"flex items-center gap-2"},Fa={key:0,class:"flex flex-col gap-4"},Ma={class:"flex flex-col gap-2"},Na={class:"flex flex-col gap-2"},Ra={class:"flex items-center gap-2"},Wa={key:0,class:"flex flex-col gap-4"},Za={class:"flex flex-col gap-2"},Xa={class:"flex items-center gap-2"},Ya={key:0,class:"flex flex-col gap-4"},Ga={class:"grid grid-cols-1 md:grid-cols-2 gap-4"},Qa={class:"flex flex-col gap-2"},Ja={class:"flex flex-col gap-2"},el={class:"flex flex-col gap-2"},tl={class:"flex flex-col gap-2"},nl={class:"flex flex-col gap-2"},al={class:"flex flex-col gap-2"},ll={class:"flex flex-col gap-6"},rl={class:"flex items-center gap-2"},il={key:0,class:"flex flex-col gap-6"},ol={class:"flex flex-col gap-2"},sl={key:0,class:"text-yellow-400 flex items-center gap-1"},dl={key:1,class:"text-gray-400"},ul={class:"flex flex-col gap-2"},cl={class:"flex items-center gap-4"},pl={class:"font-mono"},fl={class:"flex flex-col gap-6"},bl={class:"flex flex-col gap-4"},gl={class:"flex flex-col gap-2"},vl={class:"flex items-center gap-2 mt-2"},ml={class:"flex items-center gap-2"},hl={key:0,class:"flex flex-col gap-4"},yl={class:"bg-yellow-900/20 border border-yellow-600/50 p-3 rounded text-yellow-200 text-sm flex items-start gap-2"},wl={class:"grid grid-cols-1 md:grid-cols-2 gap-6"},xl={class:"flex flex-col gap-2"},kl={class:"flex flex-col gap-2"},Pl={class:"grid grid-cols-1 xl:grid-cols-2 gap-6"},Sl={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},Tl={class:"flex items-center justify-between bg-gray-900/50 p-3 rounded"},Vl={class:"font-mono"},Al={class:"text-right"},$l={class:"font-mono text-green-400"},Bl={class:"flex items-center gap-2 mt-2"},Il={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3"},Cl={class:"flex gap-2"},Dl={class:"mt-2 max-h-40 overflow-y-auto"},Ll={class:"truncate"},El={class:"flex gap-1"},_l={class:"bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-3 xl:col-span-2"},zl={class:"flex gap-4"},Ol={class:"flex gap-4 mt-4 justify-end border-t border-gray-700 pt-4 sticky bottom-0 bg-gray-900/90 backdrop-blur p-4 z-10"},Kl={class:"flex flex-col gap-4"},Xl={__name:"Config",setup(t){const e=y({idm:{host:"",port:502,circuits:["A"],zones:[]},metrics:{url:""},web:{write_enabled:!1},logging:{interval:60,realtime_mode:!1},mqtt:{enabled:!1,broker:"",port:1883,username:"",topic_prefix:"idm/heatpump",qos:0,use_tls:!1,publish_interval:60,ha_discovery_enabled:!1,ha_discovery_prefix:"homeassistant"},network_security:{enabled:!1,whitelist:[],blacklist:[]},signal:{enabled:!1,cli_path:"signal-cli",sender:"",recipients:[]},telegram:{enabled:!1,bot_token:"",chat_ids:[]},discord:{enabled:!1,webhook_url:""},email:{enabled:!1,smtp_server:"",smtp_port:587,username:"",sender:"",recipients:[]},ai:{enabled:!1,sensitivity:3,model:"rolling"},updates:{enabled:!1,interval_hours:12,mode:"apply",target:"all"}}),n=y([{label:"Statistisch (Rolling Window)",value:"rolling"},{label:"Isolation Forest (Expert)",value:"isolation_forest"}]),l=y(""),s=y(""),r=y(""),c=y(""),p=y(""),m=y(""),P=y(""),D=y(""),ae=y({}),He=y({}),ke=y(!1),Pe=y(""),Se=y(!0),le=y(!1),w=rt(),re=it(),Te=y([]),Ve=y(!1),ie=y(!1),Ae=y(!1),H=y(null),oe=y(null),q=y(!1),F=y(""),se=y(!1);ot(async()=>{try{const b=await T.get("/api/config");e.value=b.data,e.value.network_security&&(c.value=(e.value.network_security.whitelist||[]).join(`
`),p.value=(e.value.network_security.blacklist||[]).join(`
`)),e.value.signal&&(m.value=(e.value.signal.recipients||[]).join(`
`)),e.value.telegram&&(P.value=(e.value.telegram.chat_ids||[]).join(", ")),e.value.email&&(D.value=(e.value.email.recipients||[]).join(", "));try{const a=await T.get("/api/health");Pe.value=a.data.client_ip||"Unbekannt"}catch(a){console.error("Failed to get client IP",a)}de(),Fe()}catch{w.add({severity:"error",summary:"Fehler",detail:"Konfiguration konnte nicht geladen werden",life:3e3})}finally{Se.value=!1}});const qe=async()=>{try{const b=await T.post("/api/signal/test",{message:"Signal Test vom IDM Metrics Collector"});b.data.success?w.add({severity:"success",summary:"Erfolg",detail:b.data.message,life:3e3}):w.add({severity:"error",summary:"Fehler",detail:b.data.error||"Signal Test fehlgeschlagen",life:3e3})}catch(b){w.add({severity:"error",summary:"Fehler",detail:b.response?.data?.error||b.message,life:5e3})}},Fe=async()=>{ke.value=!0;try{const[b,a]=await Promise.all([T.get("/api/check-update"),T.get("/api/signal/status")]);ae.value=b.data,He.value=a.data}catch{w.add({severity:"error",summary:"Fehler",detail:"Status konnte nicht geladen werden",life:3e3})}finally{ke.value=!1}},Me=async()=>{le.value=!0;try{const b={idm_host:e.value.idm.host,idm_port:e.value.idm.port,circuits:e.value.idm.circuits,zones:e.value.idm.zones,metrics_url:e.value.metrics.url,write_enabled:e.value.web.write_enabled,logging_interval:e.value.logging.interval,realtime_mode:e.value.logging.realtime_mode,mqtt_enabled:e.value.mqtt?.enabled||!1,mqtt_broker:e.value.mqtt?.broker||"",mqtt_port:e.value.mqtt?.port||1883,mqtt_username:e.value.mqtt?.username||"",mqtt_password:s.value||void 0,mqtt_topic_prefix:e.value.mqtt?.topic_prefix||"idm/heatpump",mqtt_qos:e.value.mqtt?.qos||0,mqtt_use_tls:e.value.mqtt?.use_tls||!1,mqtt_publish_interval:e.value.mqtt?.publish_interval||60,mqtt_ha_discovery_enabled:e.value.mqtt?.ha_discovery_enabled||!1,mqtt_ha_discovery_prefix:e.value.mqtt?.ha_discovery_prefix||"homeassistant",network_security_enabled:e.value.network_security?.enabled||!1,network_security_whitelist:c.value,network_security_blacklist:p.value,signal_enabled:e.value.signal?.enabled||!1,signal_sender:e.value.signal?.sender||"",signal_cli_path:e.value.signal?.cli_path||"signal-cli",signal_recipients:m.value,telegram_enabled:e.value.telegram?.enabled||!1,telegram_bot_token:e.value.telegram?.bot_token||"",telegram_chat_ids:P.value,discord_enabled:e.value.discord?.enabled||!1,discord_webhook_url:e.value.discord?.webhook_url||"",email_enabled:e.value.email?.enabled||!1,email_smtp_server:e.value.email?.smtp_server||"",email_smtp_port:e.value.email?.smtp_port||587,email_username:e.value.email?.username||"",email_password:r.value||void 0,email_sender:e.value.email?.sender||"",email_recipients:D.value,ai_enabled:e.value.ai?.enabled||!1,ai_sensitivity:e.value.ai?.sensitivity||3,ai_model:e.value.ai?.model||"rolling",updates_enabled:e.value.updates?.enabled||!1,updates_interval_hours:e.value.updates?.interval_hours||12,updates_mode:e.value.updates?.mode||"apply",updates_target:e.value.updates?.target||"all",new_password:l.value||void 0},a=await T.post("/api/config",b);w.add({severity:"success",summary:"Erfolg",detail:a.data.message||"Einstellungen erfolgreich gespeichert",life:3e3}),l.value="",s.value=""}catch(b){w.add({severity:"error",summary:"Fehler",detail:b.response?.data?.error||b.message,life:5e3})}finally{le.value=!1}},Ne=()=>{re.require({message:"Bist du sicher, dass du den Dienst neu starten möchtest?",header:"Bestätigung",icon:"pi pi-exclamation-triangle",accept:async()=>{try{const b=await T.post("/api/restart");w.add({severity:"info",summary:"Neustart",detail:b.data.message,life:3e3})}catch{w.add({severity:"error",summary:"Fehler",detail:"Neustart fehlgeschlagen",life:3e3})}}})},de=async()=>{Ve.value=!0;try{const b=await T.get("/api/backup/list");Te.value=b.data.backups||[]}catch{w.add({severity:"error",summary:"Fehler",detail:"Backups konnten nicht geladen werden",life:3e3})}finally{Ve.value=!1}},Re=async()=>{ie.value=!0;try{const b=await T.post("/api/backup/create");b.data.success?(w.add({severity:"success",summary:"Erfolg",detail:`Backup erstellt: ${b.data.filename}`,life:3e3}),de()):w.add({severity:"error",summary:"Fehler",detail:b.data.error,life:3e3})}catch(b){w.add({severity:"error",summary:"Fehler",detail:b.response?.data?.error||"Backup Erstellung fehlgeschlagen",life:3e3})}finally{ie.value=!1}},We=async b=>{try{const a=await T.get(`/api/backup/download/${b}`,{responseType:"blob"}),o=window.URL.createObjectURL(new Blob([a.data])),B=document.createElement("a");B.href=o,B.setAttribute("download",b),document.body.appendChild(B),B.click(),B.remove(),w.add({severity:"success",summary:"Erfolg",detail:"Backup heruntergeladen",life:2e3})}catch{w.add({severity:"error",summary:"Fehler",detail:"Backup Download fehlgeschlagen",life:3e3})}},Ze=b=>{re.require({message:`Backup "${b}" löschen?`,header:"Backup Löschen",icon:"pi pi-trash",acceptClass:"p-button-danger",accept:async()=>{try{await T.delete(`/api/backup/delete/${b}`),w.add({severity:"success",summary:"Erfolg",detail:"Backup gelöscht",life:2e3}),de()}catch{w.add({severity:"error",summary:"Fehler",detail:"Backup löschen fehlgeschlagen",life:3e3})}}})},Xe=b=>{const a=b.target.files[0];H.value=a},Ye=async()=>{H.value&&re.require({message:"Konfiguration aus hochgeladener Datei wiederherstellen? Dies überschreibt deine aktuellen Einstellungen!",header:"Aus Datei Wiederherstellen",icon:"pi pi-exclamation-triangle",acceptClass:"p-button-warning",accept:async()=>{Ae.value=!0;try{const b=new FormData;b.append("file",H.value),b.append("restore_secrets","false");const a=await T.post("/api/backup/restore",b,{headers:{"Content-Type":"multipart/form-data"}});a.data.success?(w.add({severity:"success",summary:"Erfolg",detail:a.data.message,life:5e3}),H.value=null,oe.value&&(oe.value.value=""),setTimeout(()=>location.reload(),2e3)):w.add({severity:"error",summary:"Fehler",detail:a.data.error,life:5e3})}catch(b){w.add({severity:"error",summary:"Fehler",detail:b.response?.data?.error||"Wiederherstellung fehlgeschlagen",life:5e3})}finally{Ae.value=!1}}})},Ge=async()=>{if(F.value==="DELETE"){se.value=!0;try{const b=await T.post("/api/database/delete");b.data.success?(w.add({severity:"success",summary:"Erfolg",detail:b.data.message,life:5e3}),q.value=!1,F.value=""):w.add({severity:"error",summary:"Fehler",detail:b.data.error,life:5e3})}catch(b){w.add({severity:"error",summary:"Fehler",detail:b.response?.data?.error||"Datenbank löschen fehlgeschlagen",life:5e3})}finally{se.value=!1}}};return(b,a)=>(f(),g("div",aa,[a[101]||(a[101]=i("h1",{class:"text-2xl font-bold mb-4"},"Konfiguration",-1)),Se.value?(f(),g("div",la,[...a[46]||(a[46]=[i("i",{class:"pi pi-spin pi-spinner text-4xl"},null,-1)])])):(f(),g("div",ra,[u(d(Oe),null,{default:h(()=>[u(d(O),{header:"Verbindung"},{default:h(()=>[i("div",ia,[u(d(A),{legend:"IDM Wärmepumpe",toggleable:!0},{default:h(()=>[i("div",oa,[i("div",sa,[i("div",da,[a[47]||(a[47]=i("label",null,"Host / IP",-1)),u(d(k),{modelValue:e.value.idm.host,"onUpdate:modelValue":a[0]||(a[0]=o=>e.value.idm.host=o),class:"w-full"},null,8,["modelValue"])]),i("div",ua,[a[48]||(a[48]=i("label",null,"Port",-1)),u(d(J),{modelValue:e.value.idm.port,"onUpdate:modelValue":a[1]||(a[1]=o=>e.value.idm.port=o),useGrouping:!1,class:"w-full"},null,8,["modelValue"])])]),i("div",ca,[a[50]||(a[50]=i("label",{class:"font-bold"},"Aktivierte Heizkreise",-1)),i("div",pa,[i("div",fa,[u(d(S),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":a[2]||(a[2]=o=>e.value.idm.circuits=o),inputId:"circuitA",value:"A",disabled:""},null,8,["modelValue"]),a[49]||(a[49]=i("label",{for:"circuitA",class:"opacity-50"},"Heizkreis A (Fest)",-1))]),(f(),g(L,null,U(["B","C","D","E","F","G"],o=>i("div",{key:o,class:"flex items-center gap-2"},[u(d(S),{modelValue:e.value.idm.circuits,"onUpdate:modelValue":a[3]||(a[3]=B=>e.value.idm.circuits=B),inputId:"circuit"+o,value:o},null,8,["modelValue","inputId","value"]),i("label",{for:"circuit"+o},"Heizkreis "+$(o),9,ba)])),64))])]),i("div",ga,[a[51]||(a[51]=i("label",{class:"font-bold"},"Zonenmodule",-1)),i("div",va,[(f(),g(L,null,U(10,o=>i("div",{key:o,class:"flex items-center gap-2"},[u(d(S),{modelValue:e.value.idm.zones,"onUpdate:modelValue":a[4]||(a[4]=B=>e.value.idm.zones=B),inputId:"zone"+(o-1),value:o-1},null,8,["modelValue","inputId","value"]),i("label",{for:"zone"+(o-1)},"Zone "+$(o),9,ma)])),64))])])])]),_:1}),u(d(A),{legend:"Datenbank (VictoriaMetrics)",toggleable:!0},{default:h(()=>[i("div",ha,[i("div",ya,[a[52]||(a[52]=i("label",null,"Write URL",-1)),u(d(k),{modelValue:e.value.metrics.url,"onUpdate:modelValue":a[5]||(a[5]=o=>e.value.metrics.url=o),class:"w-full"},null,8,["modelValue"]),a[53]||(a[53]=i("small",{class:"text-gray-300"},"Standard: http://victoriametrics:8428/write",-1))])])]),_:1}),u(d(A),{legend:"Datenerfassung",toggleable:!0},{default:h(()=>[i("div",wa,[i("div",xa,[u(d(S),{modelValue:e.value.logging.realtime_mode,"onUpdate:modelValue":a[6]||(a[6]=o=>e.value.logging.realtime_mode=o),binary:"",inputId:"realtime_mode"},null,8,["modelValue"]),a[54]||(a[54]=i("div",{class:"flex flex-col"},[i("label",{for:"realtime_mode",class:"font-bold cursor-pointer"},"Echtzeit-Modus"),i("span",{class:"text-sm text-gray-400"},"Aktualisierung im Sekundentakt (Hohe Last)")],-1))]),e.value.logging.realtime_mode?x("",!0):(f(),g("div",ka,[a[55]||(a[55]=i("label",null,"Abfrage-Intervall (Sekunden)",-1)),u(d(J),{modelValue:e.value.logging.interval,"onUpdate:modelValue":a[7]||(a[7]=o=>e.value.logging.interval=o),min:1,max:3600,useGrouping:!1,class:"w-full md:w-1/2"},null,8,["modelValue"]),a[56]||(a[56]=i("small",{class:"text-gray-400"},"Standard: 60 Sekunden",-1))]))])]),_:1})])]),_:1}),u(d(O),{header:"MQTT & Integration"},{default:h(()=>[u(d(A),{legend:"MQTT Publishing",toggleable:!1},{legend:h(()=>[i("div",Pa,[u(d(S),{modelValue:e.value.mqtt.enabled,"onUpdate:modelValue":a[8]||(a[8]=o=>e.value.mqtt.enabled=o),binary:"",inputId:"mqtt_enabled"},null,8,["modelValue"]),a[57]||(a[57]=i("span",{class:"font-bold text-lg"},"MQTT Aktivieren",-1))])]),default:h(()=>[e.value.mqtt.enabled?(f(),g("div",Sa,[i("div",Ta,[i("div",Va,[a[58]||(a[58]=i("label",null,"Broker Adresse",-1)),u(d(k),{modelValue:e.value.mqtt.broker,"onUpdate:modelValue":a[9]||(a[9]=o=>e.value.mqtt.broker=o),placeholder:"mqtt.example.com",class:"w-full"},null,8,["modelValue"])]),i("div",Aa,[a[59]||(a[59]=i("label",null,"Port",-1)),u(d(J),{modelValue:e.value.mqtt.port,"onUpdate:modelValue":a[10]||(a[10]=o=>e.value.mqtt.port=o),useGrouping:!1,min:1,max:65535,class:"w-full"},null,8,["modelValue"])]),i("div",$a,[a[60]||(a[60]=i("label",null,"Benutzername",-1)),u(d(k),{modelValue:e.value.mqtt.username,"onUpdate:modelValue":a[11]||(a[11]=o=>e.value.mqtt.username=o),placeholder:"Optional",class:"w-full"},null,8,["modelValue"])]),i("div",Ba,[a[61]||(a[61]=i("label",null,"Passwort",-1)),u(d(k),{modelValue:s.value,"onUpdate:modelValue":a[12]||(a[12]=o=>s.value=o),type:"password",placeholder:"••••••",class:"w-full"},null,8,["modelValue"])])]),i("div",Ia,[i("div",Ca,[a[62]||(a[62]=i("label",null,"Topic Präfix",-1)),u(d(k),{modelValue:e.value.mqtt.topic_prefix,"onUpdate:modelValue":a[13]||(a[13]=o=>e.value.mqtt.topic_prefix=o),class:"w-full"},null,8,["modelValue"])]),i("div",Da,[a[63]||(a[63]=i("label",null,"QoS Level",-1)),u(d(be),{modelValue:e.value.mqtt.qos,"onUpdate:modelValue":a[14]||(a[14]=o=>e.value.mqtt.qos=o),options:[0,1,2],"aria-labelledby":"basic",class:"w-full"},null,8,["modelValue"])])]),i("div",La,[i("div",Ea,[u(d(S),{modelValue:e.value.mqtt.ha_discovery_enabled,"onUpdate:modelValue":a[15]||(a[15]=o=>e.value.mqtt.ha_discovery_enabled=o),binary:"",inputId:"ha_discovery"},null,8,["modelValue"]),a[64]||(a[64]=i("label",{for:"ha_discovery",class:"font-bold text-green-400 cursor-pointer"},"Home Assistant Auto-Discovery",-1))]),e.value.mqtt.ha_discovery_enabled?(f(),g("div",_a,[a[65]||(a[65]=i("label",{class:"text-sm"},"Discovery Präfix",-1)),u(d(k),{modelValue:e.value.mqtt.ha_discovery_prefix,"onUpdate:modelValue":a[16]||(a[16]=o=>e.value.mqtt.ha_discovery_prefix=o),class:"w-full mt-1"},null,8,["modelValue"])])):x("",!0)])])):(f(),g("div",za," Aktivieren Sie MQTT, um Daten an Broker wie Mosquitto oder Home Assistant zu senden. "))]),_:1})]),_:1}),u(d(O),{header:"Benachrichtigungen"},{default:h(()=>[i("div",Oa,[u(d(A),{legend:"Signal Messenger",toggleable:!0},{legend:h(()=>[i("div",Ka,[u(d(S),{modelValue:e.value.signal.enabled,"onUpdate:modelValue":a[17]||(a[17]=o=>e.value.signal.enabled=o),binary:""},null,8,["modelValue"]),a[66]||(a[66]=i("span",{class:"font-bold"},"Signal",-1))])]),default:h(()=>[e.value.signal.enabled?(f(),g("div",ja,[i("div",Ua,[a[67]||(a[67]=i("label",null,"Sender Nummer",-1)),u(d(k),{modelValue:e.value.signal.sender,"onUpdate:modelValue":a[18]||(a[18]=o=>e.value.signal.sender=o),placeholder:"+49...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),i("div",Ha,[a[68]||(a[68]=i("label",null,"Empfänger (Pro Zeile eine Nummer)",-1)),u(d(te),{modelValue:m.value,"onUpdate:modelValue":a[19]||(a[19]=o=>m.value=o),rows:"3",class:"w-full font-mono"},null,8,["modelValue"])]),u(d(I),{label:"Testnachricht senden",icon:"pi pi-send",severity:"success",outlined:"",onClick:qe,class:"w-full md:w-auto self-start"})])):x("",!0)]),_:1}),u(d(A),{legend:"Telegram",toggleable:!0},{legend:h(()=>[i("div",qa,[u(d(S),{modelValue:e.value.telegram.enabled,"onUpdate:modelValue":a[20]||(a[20]=o=>e.value.telegram.enabled=o),binary:""},null,8,["modelValue"]),a[69]||(a[69]=i("span",{class:"font-bold"},"Telegram",-1))])]),default:h(()=>[e.value.telegram.enabled?(f(),g("div",Fa,[i("div",Ma,[a[70]||(a[70]=i("label",null,"Bot Token",-1)),u(d(k),{modelValue:e.value.telegram.bot_token,"onUpdate:modelValue":a[21]||(a[21]=o=>e.value.telegram.bot_token=o),type:"password",class:"w-full md:w-1/2"},null,8,["modelValue"])]),i("div",Na,[a[71]||(a[71]=i("label",null,"Chat IDs (Kommagetrennt)",-1)),u(d(k),{modelValue:P.value,"onUpdate:modelValue":a[22]||(a[22]=o=>P.value=o),class:"w-full md:w-1/2"},null,8,["modelValue"])])])):x("",!0)]),_:1}),u(d(A),{legend:"Discord",toggleable:!0},{legend:h(()=>[i("div",Ra,[u(d(S),{modelValue:e.value.discord.enabled,"onUpdate:modelValue":a[23]||(a[23]=o=>e.value.discord.enabled=o),binary:""},null,8,["modelValue"]),a[72]||(a[72]=i("span",{class:"font-bold"},"Discord",-1))])]),default:h(()=>[e.value.discord.enabled?(f(),g("div",Wa,[i("div",Za,[a[73]||(a[73]=i("label",null,"Webhook URL",-1)),u(d(k),{modelValue:e.value.discord.webhook_url,"onUpdate:modelValue":a[24]||(a[24]=o=>e.value.discord.webhook_url=o),type:"password",class:"w-full"},null,8,["modelValue"])])])):x("",!0)]),_:1}),u(d(A),{legend:"E-Mail",toggleable:!0},{legend:h(()=>[i("div",Xa,[u(d(S),{modelValue:e.value.email.enabled,"onUpdate:modelValue":a[25]||(a[25]=o=>e.value.email.enabled=o),binary:""},null,8,["modelValue"]),a[74]||(a[74]=i("span",{class:"font-bold"},"E-Mail",-1))])]),default:h(()=>[e.value.email.enabled?(f(),g("div",Ya,[i("div",Ga,[i("div",Qa,[a[75]||(a[75]=i("label",null,"SMTP Server",-1)),u(d(k),{modelValue:e.value.email.smtp_server,"onUpdate:modelValue":a[26]||(a[26]=o=>e.value.email.smtp_server=o),class:"w-full"},null,8,["modelValue"])]),i("div",Ja,[a[76]||(a[76]=i("label",null,"Port",-1)),u(d(J),{modelValue:e.value.email.smtp_port,"onUpdate:modelValue":a[27]||(a[27]=o=>e.value.email.smtp_port=o),useGrouping:!1,class:"w-full"},null,8,["modelValue"])]),i("div",el,[a[77]||(a[77]=i("label",null,"Benutzername",-1)),u(d(k),{modelValue:e.value.email.username,"onUpdate:modelValue":a[28]||(a[28]=o=>e.value.email.username=o),class:"w-full"},null,8,["modelValue"])]),i("div",tl,[a[78]||(a[78]=i("label",null,"Passwort",-1)),u(d(k),{modelValue:r.value,"onUpdate:modelValue":a[29]||(a[29]=o=>r.value=o),type:"password",class:"w-full"},null,8,["modelValue"])]),i("div",nl,[a[79]||(a[79]=i("label",null,"Absender Adresse",-1)),u(d(k),{modelValue:e.value.email.sender,"onUpdate:modelValue":a[30]||(a[30]=o=>e.value.email.sender=o),class:"w-full"},null,8,["modelValue"])])]),i("div",al,[a[80]||(a[80]=i("label",null,"Empfänger (Kommagetrennt)",-1)),u(d(k),{modelValue:D.value,"onUpdate:modelValue":a[31]||(a[31]=o=>D.value=o),class:"w-full"},null,8,["modelValue"])])])):x("",!0)]),_:1})])]),_:1}),u(d(O),{header:"KI-Analyse"},{default:h(()=>[i("div",ll,[u(d(A),{legend:"KI & Anomalieerkennung",toggleable:!0},{legend:h(()=>[i("div",rl,[u(d(S),{modelValue:e.value.ai.enabled,"onUpdate:modelValue":a[32]||(a[32]=o=>e.value.ai.enabled=o),binary:""},null,8,["modelValue"]),a[81]||(a[81]=i("span",{class:"font-bold"},"KI-Analyse aktivieren",-1))])]),default:h(()=>[e.value.ai.enabled?(f(),g("div",il,[i("div",ol,[a[83]||(a[83]=i("label",{class:"font-bold"},"Modell-Typ",-1)),u(d(be),{modelValue:e.value.ai.model,"onUpdate:modelValue":a[33]||(a[33]=o=>e.value.ai.model=o),options:n.value,optionLabel:"label",optionValue:"value","aria-labelledby":"basic",class:"w-full md:w-1/2"},null,8,["modelValue","options"]),e.value.ai.model==="isolation_forest"?(f(),g("small",sl,[...a[82]||(a[82]=[i("i",{class:"pi pi-exclamation-triangle"},null,-1),E(' Achtung: "Isolation Forest" benötigt viel RAM/CPU. Nicht für Raspberry Pi Zero/3 empfohlen! ',-1)])])):(f(),g("small",dl," Standard: Gleitendes Fenster für flexible Anpassung an Jahreszeiten. "))]),i("div",ul,[a[84]||(a[84]=i("label",null,"Sensitivität (Sigma)",-1)),i("div",cl,[u(d(Ue),{modelValue:e.value.ai.sensitivity,"onUpdate:modelValue":a[34]||(a[34]=o=>e.value.ai.sensitivity=o),min:1,max:10,step:.1,class:"w-full md:w-1/2"},null,8,["modelValue"]),i("span",pl,$(e.value.ai.sensitivity)+" σ",1)]),a[85]||(a[85]=i("small",{class:"text-gray-400"},"Höherer Wert = Weniger Alarme (nur extreme Abweichungen).",-1))])])):x("",!0)]),_:1})])]),_:1}),u(d(O),{header:"Sicherheit"},{default:h(()=>[i("div",fl,[u(d(A),{legend:"Webzugriff",toggleable:!0},{default:h(()=>[i("div",bl,[i("div",gl,[a[86]||(a[86]=i("label",null,"Admin Passwort ändern",-1)),u(d(k),{modelValue:l.value,"onUpdate:modelValue":a[35]||(a[35]=o=>l.value=o),type:"password",placeholder:"Neues Passwort eingeben...",class:"w-full md:w-1/2"},null,8,["modelValue"])]),i("div",vl,[u(d(S),{modelValue:e.value.web.write_enabled,"onUpdate:modelValue":a[36]||(a[36]=o=>e.value.web.write_enabled=o),binary:"",inputId:"write_access"},null,8,["modelValue"]),a[87]||(a[87]=i("div",{class:"flex flex-col"},[i("label",{for:"write_access",class:"font-bold cursor-pointer"},"Schreibzugriff erlauben"),i("span",{class:"text-sm text-gray-400"},"Erforderlich für manuelle Steuerung und Zeitpläne")],-1))])])]),_:1}),u(d(A),{legend:"Netzwerk Firewall",toggleable:!0},{legend:h(()=>[i("div",ml,[u(d(S),{modelValue:e.value.network_security.enabled,"onUpdate:modelValue":a[37]||(a[37]=o=>e.value.network_security.enabled=o),binary:""},null,8,["modelValue"]),a[88]||(a[88]=i("span",{class:"font-bold"},"IP Whitelist/Blacklist",-1))])]),default:h(()=>[e.value.network_security.enabled?(f(),g("div",hl,[i("div",yl,[a[91]||(a[91]=i("i",{class:"pi pi-exclamation-triangle mt-0.5"},null,-1)),i("span",null,[a[89]||(a[89]=E("Deine IP ist ",-1)),i("strong",null,$(Pe.value),1),a[90]||(a[90]=E(". Füge diese zur Whitelist hinzu, sonst sperrst du dich aus!",-1))])]),i("div",wl,[i("div",xl,[a[92]||(a[92]=i("label",{class:"font-bold text-green-400"},"Whitelist (Erlaubt)",-1)),u(d(te),{modelValue:c.value,"onUpdate:modelValue":a[38]||(a[38]=o=>c.value=o),rows:"5",class:"w-full font-mono text-sm",placeholder:"192.168.1.0/24"},null,8,["modelValue"])]),i("div",kl,[a[93]||(a[93]=i("label",{class:"font-bold text-red-400"},"Blacklist (Blockiert)",-1)),u(d(te),{modelValue:p.value,"onUpdate:modelValue":a[39]||(a[39]=o=>p.value=o),rows:"5",class:"w-full font-mono text-sm",placeholder:"1.2.3.4"},null,8,["modelValue"])])])])):x("",!0)]),_:1})])]),_:1}),u(d(O),{header:"System & Wartung"},{default:h(()=>[i("div",Pl,[i("div",Sl,[a[97]||(a[97]=i("h3",{class:"font-bold text-lg flex items-center gap-2"},[i("i",{class:"pi pi-refresh"}),E(" Update Status ")],-1)),i("div",Tl,[i("div",null,[a[94]||(a[94]=i("div",{class:"text-sm text-gray-400"},"Installierte Version",-1)),i("div",Vl,$(ae.value.current_version||"v0.0.0"),1)]),i("div",Al,[a[95]||(a[95]=i("div",{class:"text-sm text-gray-400"},"Verfügbare Version",-1)),i("div",$l,$(ae.value.latest_version||"Checking..."),1)])]),i("div",Bl,[u(d(S),{modelValue:e.value.updates.enabled,"onUpdate:modelValue":a[40]||(a[40]=o=>e.value.updates.enabled=o),binary:"",inputId:"auto_updates"},null,8,["modelValue"]),a[96]||(a[96]=i("label",{for:"auto_updates"},"Auto-Updates aktivieren",-1))])]),i("div",Il,[a[98]||(a[98]=i("h3",{class:"font-bold text-lg flex items-center gap-2"},[i("i",{class:"pi pi-database"}),E(" Backup ")],-1)),i("div",Cl,[u(d(I),{label:"Backup erstellen",icon:"pi pi-download",size:"small",onClick:Re,loading:ie.value},null,8,["loading"]),u(d(I),{label:"Backup hochladen",icon:"pi pi-upload",size:"small",severity:"secondary",onClick:a[41]||(a[41]=o=>b.$refs.fileInput.click())}),i("input",{type:"file",ref_key:"fileInput",ref:oe,class:"hidden",onChange:Xe,accept:".zip"},null,544)]),H.value?(f(),z(d(I),{key:0,label:"Wiederherstellen starten",severity:"warning",class:"w-full mt-2",onClick:Ye})):x("",!0),i("div",Dl,[(f(!0),g(L,null,U(Te.value,o=>(f(),g("div",{key:o.filename,class:"flex justify-between items-center p-2 hover:bg-gray-700 rounded text-sm border-b border-gray-700 last:border-0"},[i("span",Ll,$(o.filename),1),i("div",El,[u(d(I),{icon:"pi pi-download",text:"",size:"small",onClick:B=>We(o.filename)},null,8,["onClick"]),u(d(I),{icon:"pi pi-trash",text:"",severity:"danger",size:"small",onClick:B=>Ze(o.filename)},null,8,["onClick"])])]))),128))])]),i("div",_l,[a[99]||(a[99]=i("h3",{class:"font-bold text-lg flex items-center gap-2 text-red-400"},[i("i",{class:"pi pi-power-off"}),E(" Danger Zone ")],-1)),i("div",zl,[u(d(I),{label:"Dienst neu starten",icon:"pi pi-refresh",severity:"warning",onClick:Ne}),u(d(I),{label:"Datenbank löschen",icon:"pi pi-trash",severity:"danger",onClick:a[42]||(a[42]=o=>q.value=!0)})])])])]),_:1})]),_:1})])),i("div",Ol,[u(d(I),{label:"Speichern",icon:"pi pi-save",onClick:Me,loading:le.value,size:"large",severity:"primary"},null,8,["loading"])]),u(d(pt),{visible:q.value,"onUpdate:visible":a[45]||(a[45]=o=>q.value=o),modal:"",header:"Datenbank löschen",style:{width:"450px"}},{footer:h(()=>[u(d(I),{label:"Abbrechen",text:"",onClick:a[44]||(a[44]=o=>q.value=!1)}),u(d(I),{label:"Alles löschen",severity:"danger",onClick:Ge,disabled:F.value!=="DELETE",loading:se.value},null,8,["disabled","loading"])]),default:h(()=>[i("div",Kl,[a[100]||(a[100]=i("div",{class:"flex items-start gap-3"},[i("i",{class:"pi pi-exclamation-triangle text-red-500 text-2xl"}),i("div",{class:"flex flex-col gap-2"},[i("span",{class:"font-bold text-lg"},"Bist du dir absolut sicher?"),i("p",{class:"text-gray-300"},[E(" Diese Aktion löscht "),i("span",{class:"font-bold text-red-400"},"ALLE"),E(" Daten dauerhaft aus der Datenbank. ")])])],-1)),u(d(k),{modelValue:F.value,"onUpdate:modelValue":a[43]||(a[43]=o=>F.value=o),placeholder:"Tippe DELETE",class:"w-full"},null,8,["modelValue"])])]),_:1},8,["visible"]),u(d(ut)),u(d(ct))]))}};export{Xl as default};
