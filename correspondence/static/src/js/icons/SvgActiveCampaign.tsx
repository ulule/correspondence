import * as React from "react";

type SvgActiveCampaignProps = {
  [key: string]: any
}

export default function SvgActiveCampaign(props: SvgActiveCampaignProps): React.ReactElement {
  return (
    <svg viewBox="0 0 384 384" height="1em" width="1em" {...props}>
      <defs>
        <clipPath id="active-campaign_svg__a" clipPathUnits="userSpaceOnUse">
          <path d="M0 288h288V0H0z" />
        </clipPath>
      </defs>
      <g
        clipPath="url(#active-campaign_svg__a)"
        transform="matrix(1.33333 0 0 -1.33333 0 384)"
      >
        <path
          d="M126.676 133.018c4.392 0 8.806 1.724 13.52 5.179 5.514 3.857 10.476 7.166 10.482 7.173l1.691 1.127-1.668 1.156c-.74.519-74.218 51.506-81.825 56.394-3.509 2.549-7.529 3.095-10.75 1.453-3-1.53-4.724-4.682-4.724-8.655V179.53l.595-.412c.51-.353 51.007-35.477 60.857-42.047 4.056-2.7 7.93-4.054 11.822-4.054"
          fill="#fff"
        />
        <path
          d="M225.195 163.527C220.8 166.817 63.18 276.679 56.471 281.353l-2.17 1.516v-26.983c0-8.585 4.487-11.834 10.173-15.95 0 0 120.91-84.263 135.898-94.665-15.09-10.46-128.87-89.356-136.052-93.97-8.61-5.734-9.465-9.455-9.465-17.19V5.13s166.657 119.262 170.313 121.874l.027.016c7.59 5.699 9.322 12.515 9.398 17.354l.004 3.112c0 6.275-3.174 11.679-9.402 16.04"
          fill="#fff"
        />
      </g>
    </svg>
  );
}
