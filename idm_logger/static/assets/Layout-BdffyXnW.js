import{a as d,o as m,f as p,m as c,B as te,z as y,A as E,M as V,Y as ne,C as P,D as v,J as ie,E as G,k as S,l as N,F as K,x as re,h as g,g as k,q as H,n as w,s as C,t as U,G as oe,p as A,b as I,H as se,I as ae,_ as ue,r as _,w as x,T as me,u as le,c as F,e as ce,K as de,L as be,d as M}from"./index-mB4EineT.js";import{u as fe}from"./ui-CFV8ye2Y.js";import{x as O}from"./index-CLs7nh7g.js";import{b as q,R as he,a as Z,s as B}from"./index-CNTwlNF5.js";import{s as pe}from"./index-Dl2_alcG.js";import{A as Ie}from"./AppFooter-DJh2_xi1.js";var W={name:"BarsIcon",extends:q};function ge(t){return xe(t)||ke(t)||ye(t)||ve()}function ve(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function ye(t,e){if(t){if(typeof t=="string")return D(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?D(t,e):void 0}}function ke(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function xe(t){if(Array.isArray(t))return D(t)}function D(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,i=Array(e);n<e;n++)i[n]=t[n];return i}function we(t,e,n,i,s,r){return m(),d("svg",c({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),ge(e[0]||(e[0]=[p("path",{"fill-rule":"evenodd","clip-rule":"evenodd",d:"M13.3226 3.6129H0.677419C0.497757 3.6129 0.325452 3.54152 0.198411 3.41448C0.0713707 3.28744 0 3.11514 0 2.93548C0 2.75581 0.0713707 2.58351 0.198411 2.45647C0.325452 2.32943 0.497757 2.25806 0.677419 2.25806H13.3226C13.5022 2.25806 13.6745 2.32943 13.8016 2.45647C13.9286 2.58351 14 2.75581 14 2.93548C14 3.11514 13.9286 3.28744 13.8016 3.41448C13.6745 3.54152 13.5022 3.6129 13.3226 3.6129ZM13.3226 7.67741H0.677419C0.497757 7.67741 0.325452 7.60604 0.198411 7.479C0.0713707 7.35196 0 7.17965 0 6.99999C0 6.82033 0.0713707 6.64802 0.198411 6.52098C0.325452 6.39394 0.497757 6.32257 0.677419 6.32257H13.3226C13.5022 6.32257 13.6745 6.39394 13.8016 6.52098C13.9286 6.64802 14 6.82033 14 6.99999C14 7.17965 13.9286 7.35196 13.8016 7.479C13.6745 7.60604 13.5022 7.67741 13.3226 7.67741ZM0.677419 11.7419H13.3226C13.5022 11.7419 13.6745 11.6706 13.8016 11.5435C13.9286 11.4165 14 11.2442 14 11.0645C14 10.8848 13.9286 10.7125 13.8016 10.5855C13.6745 10.4585 13.5022 10.3871 13.3226 10.3871H0.677419C0.497757 10.3871 0.325452 10.4585 0.198411 10.5855C0.0713707 10.7125 0 10.8848 0 11.0645C0 11.2442 0.0713707 11.4165 0.198411 11.5435C0.325452 11.6706 0.497757 11.7419 0.677419 11.7419Z",fill:"currentColor"},null,-1)])),16)}W.render=we;var Le=`
    .p-menubar {
        display: flex;
        align-items: center;
        background: dt('menubar.background');
        border: 1px solid dt('menubar.border.color');
        border-radius: dt('menubar.border.radius');
        color: dt('menubar.color');
        padding: dt('menubar.padding');
        gap: dt('menubar.gap');
    }

    .p-menubar-start,
    .p-megamenu-end {
        display: flex;
        align-items: center;
    }

    .p-menubar-root-list,
    .p-menubar-submenu {
        display: flex;
        margin: 0;
        padding: 0;
        list-style: none;
        outline: 0 none;
    }

    .p-menubar-root-list {
        align-items: center;
        flex-wrap: wrap;
        gap: dt('menubar.gap');
    }

    .p-menubar-root-list > .p-menubar-item > .p-menubar-item-content {
        border-radius: dt('menubar.base.item.border.radius');
    }

    .p-menubar-root-list > .p-menubar-item > .p-menubar-item-content > .p-menubar-item-link {
        padding: dt('menubar.base.item.padding');
    }

    .p-menubar-item-content {
        transition:
            background dt('menubar.transition.duration'),
            color dt('menubar.transition.duration');
        border-radius: dt('menubar.item.border.radius');
        color: dt('menubar.item.color');
    }

    .p-menubar-item-link {
        cursor: pointer;
        display: flex;
        align-items: center;
        text-decoration: none;
        overflow: hidden;
        position: relative;
        color: inherit;
        padding: dt('menubar.item.padding');
        gap: dt('menubar.item.gap');
        user-select: none;
        outline: 0 none;
    }

    .p-menubar-item-label {
        line-height: 1;
    }

    .p-menubar-item-icon {
        color: dt('menubar.item.icon.color');
    }

    .p-menubar-submenu-icon {
        color: dt('menubar.submenu.icon.color');
        margin-left: auto;
        font-size: dt('menubar.submenu.icon.size');
        width: dt('menubar.submenu.icon.size');
        height: dt('menubar.submenu.icon.size');
    }

    .p-menubar-submenu .p-menubar-submenu-icon:dir(rtl) {
        margin-left: 0;
        margin-right: auto;
    }

    .p-menubar-item.p-focus > .p-menubar-item-content {
        color: dt('menubar.item.focus.color');
        background: dt('menubar.item.focus.background');
    }

    .p-menubar-item.p-focus > .p-menubar-item-content .p-menubar-item-icon {
        color: dt('menubar.item.icon.focus.color');
    }

    .p-menubar-item.p-focus > .p-menubar-item-content .p-menubar-submenu-icon {
        color: dt('menubar.submenu.icon.focus.color');
    }

    .p-menubar-item:not(.p-disabled) > .p-menubar-item-content:hover {
        color: dt('menubar.item.focus.color');
        background: dt('menubar.item.focus.background');
    }

    .p-menubar-item:not(.p-disabled) > .p-menubar-item-content:hover .p-menubar-item-icon {
        color: dt('menubar.item.icon.focus.color');
    }

    .p-menubar-item:not(.p-disabled) > .p-menubar-item-content:hover .p-menubar-submenu-icon {
        color: dt('menubar.submenu.icon.focus.color');
    }

    .p-menubar-item-active > .p-menubar-item-content {
        color: dt('menubar.item.active.color');
        background: dt('menubar.item.active.background');
    }

    .p-menubar-item-active > .p-menubar-item-content .p-menubar-item-icon {
        color: dt('menubar.item.icon.active.color');
    }

    .p-menubar-item-active > .p-menubar-item-content .p-menubar-submenu-icon {
        color: dt('menubar.submenu.icon.active.color');
    }

    .p-menubar-submenu {
        display: none;
        position: absolute;
        min-width: 12.5rem;
        z-index: 1;
        background: dt('menubar.submenu.background');
        border: 1px solid dt('menubar.submenu.border.color');
        border-radius: dt('menubar.submenu.border.radius');
        box-shadow: dt('menubar.submenu.shadow');
        color: dt('menubar.submenu.color');
        flex-direction: column;
        padding: dt('menubar.submenu.padding');
        gap: dt('menubar.submenu.gap');
    }

    .p-menubar-submenu .p-menubar-separator {
        border-block-start: 1px solid dt('menubar.separator.border.color');
    }

    .p-menubar-submenu .p-menubar-item {
        position: relative;
    }

    .p-menubar-submenu > .p-menubar-item-active > .p-menubar-submenu {
        display: block;
        left: 100%;
        top: 0;
    }

    .p-menubar-end {
        margin-left: auto;
        align-self: center;
    }

    .p-menubar-end:dir(rtl) {
        margin-left: 0;
        margin-right: auto;
    }

    .p-menubar-button {
        display: none;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        width: dt('menubar.mobile.button.size');
        height: dt('menubar.mobile.button.size');
        position: relative;
        color: dt('menubar.mobile.button.color');
        border: 0 none;
        background: transparent;
        border-radius: dt('menubar.mobile.button.border.radius');
        transition:
            background dt('menubar.transition.duration'),
            color dt('menubar.transition.duration'),
            outline-color dt('menubar.transition.duration');
        outline-color: transparent;
    }

    .p-menubar-button:hover {
        color: dt('menubar.mobile.button.hover.color');
        background: dt('menubar.mobile.button.hover.background');
    }

    .p-menubar-button:focus-visible {
        box-shadow: dt('menubar.mobile.button.focus.ring.shadow');
        outline: dt('menubar.mobile.button.focus.ring.width') dt('menubar.mobile.button.focus.ring.style') dt('menubar.mobile.button.focus.ring.color');
        outline-offset: dt('menubar.mobile.button.focus.ring.offset');
    }

    .p-menubar-mobile {
        position: relative;
    }

    .p-menubar-mobile .p-menubar-button {
        display: flex;
    }

    .p-menubar-mobile .p-menubar-root-list {
        position: absolute;
        display: none;
        width: 100%;
        flex-direction: column;
        top: 100%;
        left: 0;
        z-index: 1;
        padding: dt('menubar.submenu.padding');
        background: dt('menubar.submenu.background');
        border: 1px solid dt('menubar.submenu.border.color');
        box-shadow: dt('menubar.submenu.shadow');
        border-radius: dt('menubar.submenu.border.radius');
        gap: dt('menubar.submenu.gap');
    }

    .p-menubar-mobile .p-menubar-root-list:dir(rtl) {
        left: auto;
        right: 0;
    }

    .p-menubar-mobile .p-menubar-root-list > .p-menubar-item > .p-menubar-item-content > .p-menubar-item-link {
        padding: dt('menubar.item.padding');
    }

    .p-menubar-mobile-active .p-menubar-root-list {
        display: flex;
    }

    .p-menubar-mobile .p-menubar-root-list .p-menubar-item {
        width: 100%;
        position: static;
    }

    .p-menubar-mobile .p-menubar-root-list .p-menubar-separator {
        border-block-start: 1px solid dt('menubar.separator.border.color');
    }

    .p-menubar-mobile .p-menubar-root-list > .p-menubar-item > .p-menubar-item-content .p-menubar-submenu-icon {
        margin-left: auto;
        transition: transform 0.2s;
    }

    .p-menubar-mobile .p-menubar-root-list > .p-menubar-item > .p-menubar-item-content .p-menubar-submenu-icon:dir(rtl),
    .p-menubar-mobile .p-menubar-submenu-icon:dir(rtl) {
        margin-left: 0;
        margin-right: auto;
    }

    .p-menubar-mobile .p-menubar-root-list > .p-menubar-item-active > .p-menubar-item-content .p-menubar-submenu-icon {
        transform: rotate(-180deg);
    }

    .p-menubar-mobile .p-menubar-submenu .p-menubar-submenu-icon {
        transition: transform 0.2s;
        transform: rotate(90deg);
    }

    .p-menubar-mobile .p-menubar-item-active > .p-menubar-item-content .p-menubar-submenu-icon {
        transform: rotate(-90deg);
    }

    .p-menubar-mobile .p-menubar-submenu {
        width: 100%;
        position: static;
        box-shadow: none;
        border: 0 none;
        padding-inline-start: dt('menubar.submenu.mobile.indent');
        padding-inline-end: 0;
    }
`,Pe={submenu:function(e){var n=e.instance,i=e.processedItem;return{display:n.isItemActive(i)?"flex":"none"}}},Ce={root:function(e){var n=e.instance;return["p-menubar p-component",{"p-menubar-mobile":n.queryMatches,"p-menubar-mobile-active":n.mobileActive}]},start:"p-menubar-start",button:"p-menubar-button",rootList:"p-menubar-root-list",item:function(e){var n=e.instance,i=e.processedItem;return["p-menubar-item",{"p-menubar-item-active":n.isItemActive(i),"p-focus":n.isItemFocused(i),"p-disabled":n.isItemDisabled(i)}]},itemContent:"p-menubar-item-content",itemLink:"p-menubar-item-link",itemIcon:"p-menubar-item-icon",itemLabel:"p-menubar-item-label",submenuIcon:"p-menubar-submenu-icon",submenu:"p-menubar-submenu",separator:"p-menubar-separator",end:"p-menubar-end"},Ae=te.extend({name:"menubar",style:Le,classes:Ce,inlineStyles:Pe}),Y={name:"AngleRightIcon",extends:q};function Me(t){return Fe(t)||Ee(t)||Se(t)||Ke()}function Ke(){throw new TypeError(`Invalid attempt to spread non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`)}function Se(t,e){if(t){if(typeof t=="string")return T(t,e);var n={}.toString.call(t).slice(8,-1);return n==="Object"&&t.constructor&&(n=t.constructor.name),n==="Map"||n==="Set"?Array.from(t):n==="Arguments"||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?T(t,e):void 0}}function Ee(t){if(typeof Symbol<"u"&&t[Symbol.iterator]!=null||t["@@iterator"]!=null)return Array.from(t)}function Fe(t){if(Array.isArray(t))return T(t)}function T(t,e){(e==null||e>t.length)&&(e=t.length);for(var n=0,i=Array(e);n<e;n++)i[n]=t[n];return i}function Oe(t,e,n,i,s,r){return m(),d("svg",c({width:"14",height:"14",viewBox:"0 0 14 14",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t.pti()),Me(e[0]||(e[0]=[p("path",{d:"M5.25 11.1728C5.14929 11.1694 5.05033 11.1455 4.9592 11.1025C4.86806 11.0595 4.78666 10.9984 4.72 10.9228C4.57955 10.7822 4.50066 10.5916 4.50066 10.3928C4.50066 10.1941 4.57955 10.0035 4.72 9.86283L7.72 6.86283L4.72 3.86283C4.66067 3.71882 4.64765 3.55991 4.68275 3.40816C4.71785 3.25642 4.79932 3.11936 4.91585 3.01602C5.03238 2.91268 5.17819 2.84819 5.33305 2.83149C5.4879 2.81479 5.64411 2.84671 5.78 2.92283L9.28 6.42283C9.42045 6.56346 9.49934 6.75408 9.49934 6.95283C9.49934 7.15158 9.42045 7.34221 9.28 7.48283L5.78 10.9228C5.71333 10.9984 5.63193 11.0595 5.5408 11.1025C5.44966 11.1455 5.35071 11.1694 5.25 11.1728Z",fill:"currentColor"},null,-1)])),16)}Y.render=Oe;var _e={name:"BaseMenubar",extends:Z,props:{model:{type:Array,default:null},buttonProps:{type:null,default:null},breakpoint:{type:String,default:"960px"},ariaLabelledby:{type:String,default:null},ariaLabel:{type:String,default:null}},style:Ae,provide:function(){return{$pcMenubar:this,$parentInstance:this}}},J={name:"MenubarSub",hostName:"Menubar",extends:Z,emits:["item-mouseenter","item-click","item-mousemove"],props:{items:{type:Array,default:null},root:{type:Boolean,default:!1},popup:{type:Boolean,default:!1},mobileActive:{type:Boolean,default:!1},templates:{type:Object,default:null},level:{type:Number,default:0},menuId:{type:String,default:null},focusedItemId:{type:String,default:null},activeItemPath:{type:Object,default:null}},list:null,methods:{getItemId:function(e){return"".concat(this.menuId,"_").concat(e.key)},getItemKey:function(e){return this.getItemId(e)},getItemProp:function(e,n,i){return e&&e.item?G(e.item[n],i):void 0},getItemLabel:function(e){return this.getItemProp(e,"label")},getItemLabelId:function(e){return"".concat(this.menuId,"_").concat(e.key,"_label")},getPTOptions:function(e,n,i){return this.ptm(i,{context:{item:e.item,index:n,active:this.isItemActive(e),focused:this.isItemFocused(e),disabled:this.isItemDisabled(e),level:this.level}})},isItemActive:function(e){return this.activeItemPath.some(function(n){return n.key===e.key})},isItemVisible:function(e){return this.getItemProp(e,"visible")!==!1},isItemDisabled:function(e){return this.getItemProp(e,"disabled")},isItemFocused:function(e){return this.focusedItemId===this.getItemId(e)},isItemGroup:function(e){return y(e.items)},onItemClick:function(e,n){this.getItemProp(n,"command",{originalEvent:e,item:n.item}),this.$emit("item-click",{originalEvent:e,processedItem:n,isFocus:!0})},onItemMouseEnter:function(e,n){this.$emit("item-mouseenter",{originalEvent:e,processedItem:n})},onItemMouseMove:function(e,n){this.$emit("item-mousemove",{originalEvent:e,processedItem:n})},getAriaPosInset:function(e){return e-this.calculateAriaSetSize.slice(0,e).length+1},getMenuItemProps:function(e,n){return{action:c({class:this.cx("itemLink"),tabindex:-1},this.getPTOptions(e,n,"itemLink")),icon:c({class:[this.cx("itemIcon"),this.getItemProp(e,"icon")]},this.getPTOptions(e,n,"itemIcon")),label:c({class:this.cx("itemLabel")},this.getPTOptions(e,n,"itemLabel")),submenuicon:c({class:this.cx("submenuIcon")},this.getPTOptions(e,n,"submenuIcon"))}}},computed:{calculateAriaSetSize:function(){var e=this;return this.items.filter(function(n){return e.isItemVisible(n)&&e.getItemProp(n,"separator")})},getAriaSetSize:function(){var e=this;return this.items.filter(function(n){return e.isItemVisible(n)&&!e.getItemProp(n,"separator")}).length}},components:{AngleRightIcon:Y,AngleDownIcon:pe},directives:{ripple:he}},De=["id","aria-label","aria-disabled","aria-expanded","aria-haspopup","aria-setsize","aria-posinset","data-p-active","data-p-focused","data-p-disabled"],Te=["onClick","onMouseenter","onMousemove"],ze=["href","target"],Ve=["id"],Be=["id"];function Re(t,e,n,i,s,r){var u=S("MenubarSub",!0),h=N("ripple");return m(),d("ul",c({class:n.level===0?t.cx("rootList"):t.cx("submenu")},n.level===0?t.ptm("rootList"):t.ptm("submenu")),[(m(!0),d(K,null,re(n.items,function(o,a){return m(),d(K,{key:r.getItemKey(o)},[r.isItemVisible(o)&&!r.getItemProp(o,"separator")?(m(),d("li",c({key:0,id:r.getItemId(o),style:r.getItemProp(o,"style"),class:[t.cx("item",{processedItem:o}),r.getItemProp(o,"class")],role:"menuitem","aria-label":r.getItemLabel(o),"aria-disabled":r.isItemDisabled(o)||void 0,"aria-expanded":r.isItemGroup(o)?r.isItemActive(o):void 0,"aria-haspopup":r.isItemGroup(o)&&!r.getItemProp(o,"to")?"menu":void 0,"aria-setsize":r.getAriaSetSize,"aria-posinset":r.getAriaPosInset(a)},{ref_for:!0},r.getPTOptions(o,a,"item"),{"data-p-active":r.isItemActive(o),"data-p-focused":r.isItemFocused(o),"data-p-disabled":r.isItemDisabled(o)}),[p("div",c({class:t.cx("itemContent"),onClick:function(b){return r.onItemClick(b,o)},onMouseenter:function(b){return r.onItemMouseEnter(b,o)},onMousemove:function(b){return r.onItemMouseMove(b,o)}},{ref_for:!0},r.getPTOptions(o,a,"itemContent")),[n.templates.item?(m(),k(C(n.templates.item),{key:1,item:o.item,root:n.root,hasSubmenu:r.getItemProp(o,"items"),label:r.getItemLabel(o),props:r.getMenuItemProps(o,a)},null,8,["item","root","hasSubmenu","label","props"])):H((m(),d("a",c({key:0,href:r.getItemProp(o,"url"),class:t.cx("itemLink"),target:r.getItemProp(o,"target"),tabindex:"-1"},{ref_for:!0},r.getPTOptions(o,a,"itemLink")),[n.templates.itemicon?(m(),k(C(n.templates.itemicon),{key:0,item:o.item,class:w(t.cx("itemIcon"))},null,8,["item","class"])):r.getItemProp(o,"icon")?(m(),d("span",c({key:1,class:[t.cx("itemIcon"),r.getItemProp(o,"icon")]},{ref_for:!0},r.getPTOptions(o,a,"itemIcon")),null,16)):g("",!0),p("span",c({id:r.getItemLabelId(o),class:t.cx("itemLabel")},{ref_for:!0},r.getPTOptions(o,a,"itemLabel")),U(r.getItemLabel(o)),17,Ve),r.getItemProp(o,"items")?(m(),d(K,{key:2},[n.templates.submenuicon?(m(),k(C(n.templates.submenuicon),{key:0,root:n.root,active:r.isItemActive(o),class:w(t.cx("submenuIcon"))},null,8,["root","active","class"])):(m(),k(C(n.root?"AngleDownIcon":"AngleRightIcon"),c({key:1,class:t.cx("submenuIcon")},{ref_for:!0},r.getPTOptions(o,a,"submenuIcon")),null,16,["class"]))],64)):g("",!0)],16,ze)),[[h]])],16,Te),r.isItemVisible(o)&&r.isItemGroup(o)?(m(),k(u,{key:0,id:r.getItemId(o)+"_list",menuId:n.menuId,role:"menu",style:oe(t.sx("submenu",!0,{processedItem:o})),focusedItemId:n.focusedItemId,items:o.items,mobileActive:n.mobileActive,activeItemPath:n.activeItemPath,templates:n.templates,level:n.level+1,"aria-labelledby":r.getItemLabelId(o),pt:t.pt,unstyled:t.unstyled,onItemClick:e[0]||(e[0]=function(l){return t.$emit("item-click",l)}),onItemMouseenter:e[1]||(e[1]=function(l){return t.$emit("item-mouseenter",l)}),onItemMousemove:e[2]||(e[2]=function(l){return t.$emit("item-mousemove",l)})},null,8,["id","menuId","style","focusedItemId","items","mobileActive","activeItemPath","templates","level","aria-labelledby","pt","unstyled"])):g("",!0)],16,De)):g("",!0),r.isItemVisible(o)&&r.getItemProp(o,"separator")?(m(),d("li",c({key:1,id:r.getItemId(o),class:[t.cx("separator"),r.getItemProp(o,"class")],style:r.getItemProp(o,"style"),role:"separator"},{ref_for:!0},t.ptm("separator")),null,16,Be)):g("",!0)],64)}),128))],16)}J.render=Re;var Q={name:"Menubar",extends:_e,inheritAttrs:!1,emits:["focus","blur"],matchMediaListener:null,data:function(){return{mobileActive:!1,focused:!1,focusedItemInfo:{index:-1,level:0,parentKey:""},activeItemPath:[],dirty:!1,query:null,queryMatches:!1}},watch:{activeItemPath:function(e){y(e)?(this.bindOutsideClickListener(),this.bindResizeListener()):(this.unbindOutsideClickListener(),this.unbindResizeListener())}},outsideClickListener:null,container:null,menubar:null,mounted:function(){this.bindMatchMediaListener()},beforeUnmount:function(){this.mobileActive=!1,this.unbindOutsideClickListener(),this.unbindResizeListener(),this.unbindMatchMediaListener(),this.container&&O.clear(this.container),this.container=null},methods:{getItemProp:function(e,n){return e?G(e[n]):void 0},getItemLabel:function(e){return this.getItemProp(e,"label")},isItemDisabled:function(e){return this.getItemProp(e,"disabled")},isItemVisible:function(e){return this.getItemProp(e,"visible")!==!1},isItemGroup:function(e){return y(this.getItemProp(e,"items"))},isItemSeparator:function(e){return this.getItemProp(e,"separator")},getProccessedItemLabel:function(e){return e?this.getItemLabel(e.item):void 0},isProccessedItemGroup:function(e){return e&&y(e.items)},toggle:function(e){var n=this;this.mobileActive?(this.mobileActive=!1,O.clear(this.menubar),this.hide()):(this.mobileActive=!0,O.set("menu",this.menubar,this.$primevue.config.zIndex.menu),setTimeout(function(){n.show()},1)),this.bindOutsideClickListener(),e.preventDefault()},show:function(){v(this.menubar)},hide:function(e,n){var i=this;this.mobileActive&&(this.mobileActive=!1,setTimeout(function(){v(i.$refs.menubutton)},0)),this.activeItemPath=[],this.focusedItemInfo={index:-1,level:0,parentKey:""},n&&v(this.menubar),this.dirty=!1},onFocus:function(e){this.focused=!0,this.focusedItemInfo=this.focusedItemInfo.index!==-1?this.focusedItemInfo:{index:this.findFirstFocusedItemIndex(),level:0,parentKey:""},this.$emit("focus",e)},onBlur:function(e){this.focused=!1,this.focusedItemInfo={index:-1,level:0,parentKey:""},this.searchValue="",this.dirty=!1,this.$emit("blur",e)},onKeyDown:function(e){var n=e.metaKey||e.ctrlKey;switch(e.code){case"ArrowDown":this.onArrowDownKey(e);break;case"ArrowUp":this.onArrowUpKey(e);break;case"ArrowLeft":this.onArrowLeftKey(e);break;case"ArrowRight":this.onArrowRightKey(e);break;case"Home":this.onHomeKey(e);break;case"End":this.onEndKey(e);break;case"Space":this.onSpaceKey(e);break;case"Enter":case"NumpadEnter":this.onEnterKey(e);break;case"Escape":this.onEscapeKey(e);break;case"Tab":this.onTabKey(e);break;case"PageDown":case"PageUp":case"Backspace":case"ShiftLeft":case"ShiftRight":break;default:!n&&ie(e.key)&&this.searchItems(e,e.key);break}},onItemChange:function(e,n){var i=e.processedItem,s=e.isFocus;if(!P(i)){var r=i.index,u=i.key,h=i.level,o=i.parentKey,a=i.items,l=y(a),b=this.activeItemPath.filter(function(f){return f.parentKey!==o&&f.parentKey!==u});l&&b.push(i),this.focusedItemInfo={index:r,level:h,parentKey:o},l&&(this.dirty=!0),s&&v(this.menubar),!(n==="hover"&&this.queryMatches)&&(this.activeItemPath=b)}},onItemClick:function(e){var n=e.originalEvent,i=e.processedItem,s=this.isProccessedItemGroup(i),r=P(i.parent),u=this.isSelected(i);if(u){var h=i.index,o=i.key,a=i.level,l=i.parentKey;this.activeItemPath=this.activeItemPath.filter(function(f){return o!==f.key&&o.startsWith(f.key)}),this.focusedItemInfo={index:h,level:a,parentKey:l},this.dirty=!r,v(this.menubar)}else if(s)this.onItemChange(e);else{var b=r?i:this.activeItemPath.find(function(f){return f.parentKey===""});this.hide(n),this.changeFocusedItemIndex(n,b?b.index:-1),this.mobileActive=!1,v(this.menubar)}},onItemMouseEnter:function(e){this.dirty&&this.onItemChange(e,"hover")},onItemMouseMove:function(e){this.focused&&this.changeFocusedItemIndex(e,e.processedItem.index)},menuButtonClick:function(e){this.toggle(e)},menuButtonKeydown:function(e){(e.code==="Enter"||e.code==="NumpadEnter"||e.code==="Space")&&this.menuButtonClick(e)},onArrowDownKey:function(e){var n=this.visibleItems[this.focusedItemInfo.index],i=n?P(n.parent):null;if(i){var s=this.isProccessedItemGroup(n);s&&(this.onItemChange({originalEvent:e,processedItem:n}),this.focusedItemInfo={index:-1,parentKey:n.key},this.onArrowRightKey(e))}else{var r=this.focusedItemInfo.index!==-1?this.findNextItemIndex(this.focusedItemInfo.index):this.findFirstFocusedItemIndex();this.changeFocusedItemIndex(e,r)}e.preventDefault()},onArrowUpKey:function(e){var n=this,i=this.visibleItems[this.focusedItemInfo.index],s=P(i.parent);if(s){var r=this.isProccessedItemGroup(i);if(r){this.onItemChange({originalEvent:e,processedItem:i}),this.focusedItemInfo={index:-1,parentKey:i.key};var u=this.findLastItemIndex();this.changeFocusedItemIndex(e,u)}}else{var h=this.activeItemPath.find(function(a){return a.key===i.parentKey});if(this.focusedItemInfo.index===0)this.focusedItemInfo={index:-1,parentKey:h?h.parentKey:""},this.searchValue="",this.onArrowLeftKey(e),this.activeItemPath=this.activeItemPath.filter(function(a){return a.parentKey!==n.focusedItemInfo.parentKey});else{var o=this.focusedItemInfo.index!==-1?this.findPrevItemIndex(this.focusedItemInfo.index):this.findLastFocusedItemIndex();this.changeFocusedItemIndex(e,o)}}e.preventDefault()},onArrowLeftKey:function(e){var n=this,i=this.visibleItems[this.focusedItemInfo.index],s=i?this.activeItemPath.find(function(u){return u.key===i.parentKey}):null;if(s)this.onItemChange({originalEvent:e,processedItem:s}),this.activeItemPath=this.activeItemPath.filter(function(u){return u.parentKey!==n.focusedItemInfo.parentKey}),e.preventDefault();else{var r=this.focusedItemInfo.index!==-1?this.findPrevItemIndex(this.focusedItemInfo.index):this.findLastFocusedItemIndex();this.changeFocusedItemIndex(e,r),e.preventDefault()}},onArrowRightKey:function(e){var n=this.visibleItems[this.focusedItemInfo.index],i=n?this.activeItemPath.find(function(u){return u.key===n.parentKey}):null;if(i){var s=this.isProccessedItemGroup(n);s&&(this.onItemChange({originalEvent:e,processedItem:n}),this.focusedItemInfo={index:-1,parentKey:n.key},this.onArrowDownKey(e))}else{var r=this.focusedItemInfo.index!==-1?this.findNextItemIndex(this.focusedItemInfo.index):this.findFirstFocusedItemIndex();this.changeFocusedItemIndex(e,r),e.preventDefault()}},onHomeKey:function(e){this.changeFocusedItemIndex(e,this.findFirstItemIndex()),e.preventDefault()},onEndKey:function(e){this.changeFocusedItemIndex(e,this.findLastItemIndex()),e.preventDefault()},onEnterKey:function(e){if(this.focusedItemInfo.index!==-1){var n=E(this.menubar,'li[id="'.concat("".concat(this.focusedItemId),'"]')),i=n&&E(n,'a[data-pc-section="itemlink"]');i?i.click():n&&n.click();var s=this.visibleItems[this.focusedItemInfo.index],r=this.isProccessedItemGroup(s);!r&&(this.focusedItemInfo.index=this.findFirstFocusedItemIndex())}e.preventDefault()},onSpaceKey:function(e){this.onEnterKey(e)},onEscapeKey:function(e){if(this.focusedItemInfo.level!==0){var n=this.focusedItemInfo;this.hide(e,!1),this.focusedItemInfo={index:Number(n.parentKey.split("_")[0]),level:0,parentKey:""}}e.preventDefault()},onTabKey:function(e){if(this.focusedItemInfo.index!==-1){var n=this.visibleItems[this.focusedItemInfo.index],i=this.isProccessedItemGroup(n);!i&&this.onItemChange({originalEvent:e,processedItem:n})}this.hide()},bindOutsideClickListener:function(){var e=this;this.outsideClickListener||(this.outsideClickListener=function(n){var i=e.container&&!e.container.contains(n.target),s=!(e.target&&(e.target===n.target||e.target.contains(n.target)));i&&s&&e.hide()},document.addEventListener("click",this.outsideClickListener,!0))},unbindOutsideClickListener:function(){this.outsideClickListener&&(document.removeEventListener("click",this.outsideClickListener,!0),this.outsideClickListener=null)},bindResizeListener:function(){var e=this;this.resizeListener||(this.resizeListener=function(n){ne()||e.hide(n,!0),e.mobileActive=!1},window.addEventListener("resize",this.resizeListener))},unbindResizeListener:function(){this.resizeListener&&(window.removeEventListener("resize",this.resizeListener),this.resizeListener=null)},bindMatchMediaListener:function(){var e=this;if(!this.matchMediaListener){var n=matchMedia("(max-width: ".concat(this.breakpoint,")"));this.query=n,this.queryMatches=n.matches,this.matchMediaListener=function(){e.queryMatches=n.matches,e.mobileActive=!1},this.query.addEventListener("change",this.matchMediaListener)}},unbindMatchMediaListener:function(){this.matchMediaListener&&(this.query.removeEventListener("change",this.matchMediaListener),this.matchMediaListener=null)},isItemMatched:function(e){var n;return this.isValidItem(e)&&((n=this.getProccessedItemLabel(e))===null||n===void 0?void 0:n.toLocaleLowerCase().startsWith(this.searchValue.toLocaleLowerCase()))},isValidItem:function(e){return!!e&&!this.isItemDisabled(e.item)&&!this.isItemSeparator(e.item)&&this.isItemVisible(e.item)},isValidSelectedItem:function(e){return this.isValidItem(e)&&this.isSelected(e)},isSelected:function(e){return this.activeItemPath.some(function(n){return n.key===e.key})},findFirstItemIndex:function(){var e=this;return this.visibleItems.findIndex(function(n){return e.isValidItem(n)})},findLastItemIndex:function(){var e=this;return V(this.visibleItems,function(n){return e.isValidItem(n)})},findNextItemIndex:function(e){var n=this,i=e<this.visibleItems.length-1?this.visibleItems.slice(e+1).findIndex(function(s){return n.isValidItem(s)}):-1;return i>-1?i+e+1:e},findPrevItemIndex:function(e){var n=this,i=e>0?V(this.visibleItems.slice(0,e),function(s){return n.isValidItem(s)}):-1;return i>-1?i:e},findSelectedItemIndex:function(){var e=this;return this.visibleItems.findIndex(function(n){return e.isValidSelectedItem(n)})},findFirstFocusedItemIndex:function(){var e=this.findSelectedItemIndex();return e<0?this.findFirstItemIndex():e},findLastFocusedItemIndex:function(){var e=this.findSelectedItemIndex();return e<0?this.findLastItemIndex():e},searchItems:function(e,n){var i=this;this.searchValue=(this.searchValue||"")+n;var s=-1,r=!1;return this.focusedItemInfo.index!==-1?(s=this.visibleItems.slice(this.focusedItemInfo.index).findIndex(function(u){return i.isItemMatched(u)}),s=s===-1?this.visibleItems.slice(0,this.focusedItemInfo.index).findIndex(function(u){return i.isItemMatched(u)}):s+this.focusedItemInfo.index):s=this.visibleItems.findIndex(function(u){return i.isItemMatched(u)}),s!==-1&&(r=!0),s===-1&&this.focusedItemInfo.index===-1&&(s=this.findFirstFocusedItemIndex()),s!==-1&&this.changeFocusedItemIndex(e,s),this.searchTimeout&&clearTimeout(this.searchTimeout),this.searchTimeout=setTimeout(function(){i.searchValue="",i.searchTimeout=null},500),r},changeFocusedItemIndex:function(e,n){this.focusedItemInfo.index!==n&&(this.focusedItemInfo.index=n,this.scrollInView())},scrollInView:function(){var e=arguments.length>0&&arguments[0]!==void 0?arguments[0]:-1,n=e!==-1?"".concat(this.$id,"_").concat(e):this.focusedItemId,i=E(this.menubar,'li[id="'.concat(n,'"]'));i&&i.scrollIntoView&&i.scrollIntoView({block:"nearest",inline:"start"})},createProcessedItems:function(e){var n=this,i=arguments.length>1&&arguments[1]!==void 0?arguments[1]:0,s=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{},r=arguments.length>3&&arguments[3]!==void 0?arguments[3]:"",u=[];return e&&e.forEach(function(h,o){var a=(r!==""?r+"_":"")+o,l={item:h,index:o,level:i,key:a,parent:s,parentKey:r};l.items=n.createProcessedItems(h.items,i+1,l,a),u.push(l)}),u},containerRef:function(e){this.container=e},menubarRef:function(e){this.menubar=e?e.$el:void 0}},computed:{processedItems:function(){return this.createProcessedItems(this.model||[])},visibleItems:function(){var e=this,n=this.activeItemPath.find(function(i){return i.key===e.focusedItemInfo.parentKey});return n?n.items:this.processedItems},focusedItemId:function(){return this.focusedItemInfo.index!==-1?"".concat(this.$id).concat(y(this.focusedItemInfo.parentKey)?"_"+this.focusedItemInfo.parentKey:"","_").concat(this.focusedItemInfo.index):null}},components:{MenubarSub:J,BarsIcon:W}};function L(t){"@babel/helpers - typeof";return L=typeof Symbol=="function"&&typeof Symbol.iterator=="symbol"?function(e){return typeof e}:function(e){return e&&typeof Symbol=="function"&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},L(t)}function R(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);e&&(i=i.filter(function(s){return Object.getOwnPropertyDescriptor(t,s).enumerable})),n.push.apply(n,i)}return n}function j(t){for(var e=1;e<arguments.length;e++){var n=arguments[e]!=null?arguments[e]:{};e%2?R(Object(n),!0).forEach(function(i){je(t,i,n[i])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):R(Object(n)).forEach(function(i){Object.defineProperty(t,i,Object.getOwnPropertyDescriptor(n,i))})}return t}function je(t,e,n){return(e=Ge(e))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function Ge(t){var e=Ne(t,"string");return L(e)=="symbol"?e:e+""}function Ne(t,e){if(L(t)!="object"||!t)return t;var n=t[Symbol.toPrimitive];if(n!==void 0){var i=n.call(t,e);if(L(i)!="object")return i;throw new TypeError("@@toPrimitive must return a primitive value.")}return(e==="string"?String:Number)(t)}var He=["aria-haspopup","aria-expanded","aria-controls","aria-label"];function Ue(t,e,n,i,s,r){var u=S("BarsIcon"),h=S("MenubarSub");return m(),d("div",c({ref:r.containerRef,class:t.cx("root")},t.ptmi("root")),[t.$slots.start?(m(),d("div",c({key:0,class:t.cx("start")},t.ptm("start")),[A(t.$slots,"start")],16)):g("",!0),A(t.$slots,t.$slots.button?"button":"menubutton",{id:t.$id,class:w(t.cx("button")),toggleCallback:function(a){return r.menuButtonClick(a)}},function(){var o;return[t.model&&t.model.length>0?(m(),d("a",c({key:0,ref:"menubutton",role:"button",tabindex:"0",class:t.cx("button"),"aria-haspopup":!!(t.model.length&&t.model.length>0),"aria-expanded":s.mobileActive,"aria-controls":t.$id,"aria-label":(o=t.$primevue.config.locale.aria)===null||o===void 0?void 0:o.navigation,onClick:e[0]||(e[0]=function(a){return r.menuButtonClick(a)}),onKeydown:e[1]||(e[1]=function(a){return r.menuButtonKeydown(a)})},j(j({},t.buttonProps),t.ptm("button"))),[A(t.$slots,t.$slots.buttonicon?"buttonicon":"menubuttonicon",{},function(){return[I(u,se(ae(t.ptm("buttonicon"))),null,16)]})],16,He)):g("",!0)]}),I(h,{ref:r.menubarRef,id:t.$id+"_list",role:"menubar",items:r.processedItems,templates:t.$slots,root:!0,mobileActive:s.mobileActive,tabindex:"0","aria-activedescendant":s.focused?r.focusedItemId:void 0,menuId:t.$id,focusedItemId:s.focused?r.focusedItemId:void 0,activeItemPath:s.activeItemPath,level:0,"aria-labelledby":t.ariaLabelledby,"aria-label":t.ariaLabel,pt:t.pt,unstyled:t.unstyled,onFocus:r.onFocus,onBlur:r.onBlur,onKeydown:r.onKeyDown,onItemClick:r.onItemClick,onItemMouseenter:r.onItemMouseEnter,onItemMousemove:r.onItemMouseMove},null,8,["id","items","templates","mobileActive","aria-activedescendant","menuId","focusedItemId","activeItemPath","aria-labelledby","aria-label","pt","unstyled","onFocus","onBlur","onKeydown","onItemClick","onItemMouseenter","onItemMousemove"]),t.$slots.end?(m(),d("div",c({key:1,class:t.cx("end")},t.ptm("end")),[A(t.$slots,"end")],16)):g("",!0)],16)}Q.render=Ue;const qe={key:0,class:"fixed top-0 left-0 right-0 bg-warning-900 border-b border-warning-600 text-warning-200 p-3 z-50"},Ze={class:"fixed bottom-4 right-4 z-40"},We=["title"],Ye={__name:"NetworkStatus",setup(t){const e=_(navigator.onLine),n=_(!navigator.onLine);return window.addEventListener("online",()=>{e.value=!0,n.value=!1}),window.addEventListener("offline",()=>{e.value=!1,n.value=!0}),(i,s)=>(m(),d(K,null,[I(me,{name:"slide-down"},{default:x(()=>[n.value?(m(),d("div",qe,[...s[0]||(s[0]=[p("div",{class:"container mx-auto flex items-center gap-2"},[p("i",{class:"pi pi-wifi-slash"}),p("span",{class:"text-sm font-medium"},"Offline - Einige Funktionen sind möglicherweise nicht verfügbar")],-1)])])):g("",!0)]),_:1}),p("div",Ze,[p("div",{class:w(["w-3 h-3 rounded-full border-2 border-gray-700",e.value?"bg-success-500":"bg-error-500"]),title:e.value?"Online":"Offline"},null,10,We)])],64))}},Je=ue(Ye,[["__scopeId","data-v-d2441cce"]]),Qe={class:"flex flex-col min-h-screen"},Xe={class:"hidden sm:inline text-sm sm:text-base"},$e={class:"flex items-center gap-2"},et={class:"flex-grow container mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-4 md:py-6 lg:py-8"},at={__name:"Layout",setup(t){const e=ce(),n=le(),i=fe(),s=F(()=>i.editMode?"Bearbeiten: An":"Bearbeiten: Aus"),r=F(()=>i.editMode?"pi pi-lock-open":"pi pi-lock"),u=F(()=>i.editMode?"success":"secondary"),h=_([{label:"Dashboard",icon:"pi pi-home",command:()=>e.push("/")},{label:"Steuerung",icon:"pi pi-sliders-h",command:()=>e.push("/control")},{label:"Zeitplan",icon:"pi pi-calendar",command:()=>e.push("/schedule")},{label:"Alarme",icon:"pi pi-bell",command:()=>e.push("/alerts")},{label:"Protokolle",icon:"pi pi-list",command:()=>e.push("/logs")},{label:"Einstellungen",icon:"pi pi-cog",command:()=>e.push("/config")},{label:"Techniker",icon:"pi pi-key",command:()=>e.push("/tools")},{label:"Grafana",icon:"pi pi-chart-line",command:()=>{const b=window.location.hostname;window.open(`http://${b}:3001`,"_blank","noopener")}},{label:"Über",icon:"pi pi-info-circle",command:()=>e.push("/about")}]),o=async()=>{await n.logout(),e.push("/login")};let a;const l=()=>{clearTimeout(a),a=setTimeout(()=>{o()},3e5)};return de(()=>{i.init(),["click","mousemove","keypress","scroll","touchstart"].forEach(f=>window.addEventListener(f,l)),l()}),be(()=>{["click","mousemove","keypress","scroll","touchstart"].forEach(f=>window.removeEventListener(f,l)),clearTimeout(a)}),(b,f)=>{const X=S("router-view"),$=N("ripple");return m(),d("div",Qe,[I(Je),I(M(Q),{model:h.value,class:"rounded-none border-0 border-b border-gray-700 bg-gray-800"},{start:x(()=>[...f[0]||(f[0]=[p("span",{class:"text-lg sm:text-xl font-bold px-2 sm:px-4"},"IDM Logger",-1)])]),item:x(({item:z,props:ee})=>[H((m(),d("a",c({class:"flex items-center gap-2 px-2 sm:px-3 py-2 hover:bg-gray-700 rounded cursor-pointer transition-colors"},ee.action),[p("i",{class:w([z.icon,"text-sm sm:text-base"])},null,2),p("span",Xe,U(z.label),1)],16)),[[$]])]),end:x(()=>[p("div",$e,[I(M(B),{label:s.value,icon:r.value,severity:u.value,text:"",class:"p-2 sm:p-3",onClick:M(i).toggleEditMode},null,8,["label","icon","severity","onClick"]),I(M(B),{icon:"pi pi-power-off",severity:"danger",text:"",onClick:o,class:"p-2 sm:p-3"},{default:x(()=>[...f[1]||(f[1]=[p("span",{class:"hidden sm:inline ml-2"},"Abmelden",-1)])]),_:1})])]),_:1},8,["model"]),p("main",et,[I(X)]),I(Ie)])}}};export{at as default};
