using MediaBrowser.Common.Configuration;
using MediaBrowser.Common;
using MediaBrowser.Controller.Configuration;
using MediaBrowser.Controller.Library;
using MediaBrowser.Model.IO;
using MediaBrowser.Model.Logging;
using MediaBrowser.Model.Serialization;
using MediaBrowser.Model.Services;
using System;
using System.Collections.Generic;
using System.Text;
using MediaBrowser.Controller.Persistence;
using MediaBrowser.Controller.Entities;
using System.Threading;
using System.Collections;
using MediaBrowser.Model.Entities;
using System.Linq;

namespace ItemUpdater
{

    public class UpdateDetails
    {
        public string Type { get; set; }
        public string Value { get; set; }
    }

    // http://localhost:8096/emby/item_updater/update
    [Route("/item_updater/update", "POST", Summary = "Update Item")]
    //[Authenticated]
    public class UpdateItems : Dictionary<string, List<UpdateDetails>>, IReturn<Object>
    {
    }

    // http://localhost:8096/emby/item_updater/ping
    [Route("/item_updater/ping", "GET", Summary = "PingTest")]
    //[Authenticated]
    public class PingTest : IReturn<Object>
    {
    }

    public class ApiEndpoint : IService
    {
        private readonly ILogger _logger;
        private readonly ILibraryManager _libraryManager;
        private readonly IJsonSerializer _jsonSerializer;
        private readonly IItemRepository _itemRepository;

        public ApiEndpoint(ILogManager logger,
            ILibraryManager libraryManager,
            IJsonSerializer jsonSerializer,
            IItemRepository itemRepository)
        {
            _logger = logger.GetLogger("ItemUpdater - ApiEndpoint");
            _libraryManager = libraryManager;
            _jsonSerializer = jsonSerializer;
            _itemRepository = itemRepository;
        }

        public object Get(PingTest request)
        {
            Dictionary<string, object> responce = new Dictionary<string, object>();
            responce["message"] = "ping result";
            return responce;
        }

        public object Post(UpdateItems request)
        {
            string some_data = _jsonSerializer.SerializeToString(request);
            _logger.Info("Submitted config data : " + some_data);

            int total_updated = 0;
            int total_action = 0;
            List<BaseItem> updated_items = new List<BaseItem>();
            foreach(var item_actions in request)
            {
                bool item_updated = false;
                long emby_id = long.Parse(item_actions.Key);
                BaseItem item = _libraryManager.GetItemById(emby_id);

                if (item == null)
                {
                    _logger.Info("Item not found : " + emby_id);
                    continue;
                }

                _logger.Info("Processing changes for : " + emby_id);
                foreach (var action in item_actions.Value)
                {
                    if (action.Type.Equals("CommunityRating", StringComparison.CurrentCultureIgnoreCase))
                    {
                        double rating = double.Parse(action.Value);
                        rating = Math.Round(rating, 1);
                        int diff = (int)(rating * 10) - (int)((item.CommunityRating ?? 0) * 10);
                        if (diff != 0)
                        {
                            _logger.Info("Updating Rating " + rating);
                            item.CommunityRating = (float)rating;
                            item_updated = true;
                            total_action++;
                        }
                    }

                    if (action.Type.Equals("LockField", StringComparison.CurrentCultureIgnoreCase))
                    {
                        MetadataFields target_filed = (MetadataFields)Enum.Parse(typeof(MetadataFields), action.Value, true);
                        List<MetadataFields> metadataFields = new List<MetadataFields>(item.LockedFields);
                        if (!metadataFields.Contains(target_filed))
                        {
                            metadataFields.Add(target_filed);
                            item.LockedFields = metadataFields.ToArray();
                            item_updated = true;
                            total_action++;
                        }
                    }
                }

                if (item_updated)
                {
                    updated_items.Add(item);
                    total_updated++;
                }
            }
            
            if(updated_items.Count > 0)
            {
                CancellationToken token = CancellationToken.None;
                _itemRepository.SaveItems(updated_items, token);
            }

            Dictionary<string, object> responce = new Dictionary<string, object>();
            responce["total_items"] = total_updated;
            responce["total_actions"] = total_action;
            return responce;
        }


    }
}
