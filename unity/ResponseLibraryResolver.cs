using System;
using System.Collections.Generic;

public class ResolvedResponse
{
    public string responseCode;
    public string actionCode;
    public string text;
    public string localAudioPath;
    public bool endsConversation;
}

public class BroadGroupEntry
{
    public string groupCode;
    public ResolvedResponse preferred;
    public ResolvedResponse alternative;
}

public class ResponseLibraryResolver
{
    private readonly Dictionary<string, BroadGroupEntry> broadGroups;
    private readonly Dictionary<string, ResolvedResponse> directResponses;
    private readonly ConversationState state;

    public ResponseLibraryResolver(
        Dictionary<string, BroadGroupEntry> broadGroups,
        Dictionary<string, ResolvedResponse> directResponses,
        ConversationState state)
    {
        this.broadGroups = broadGroups;
        this.directResponses = directResponses;
        this.state = state;
    }

    public ResolvedResponse Resolve(BcRouteResult route)
    {
        if (route.routeCategory == "broad")
        {
            if (!broadGroups.TryGetValue(route.routeCode, out BroadGroupEntry group))
                throw new InvalidOperationException($"Unknown Broad route: {route.routeCode}");

            int count = state.RegisterBroadPlayback(route.routeCode);
            return (count % 2 == 1) ? group.preferred : group.alternative;
        }

        if (!directResponses.TryGetValue(route.routeCode, out ResolvedResponse response))
            throw new InvalidOperationException($"Unknown direct route: {route.routeCode}");

        if (response.endsConversation)
            state.EndConversation();

        return response;
    }
}
